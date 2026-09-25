"""Dagster definitions: dlt ingest -> dbt transform -> publish to Postgres serving layer.

Kill-switch-first:
  * Every asset calls guard() first. PIPELINE_ENABLED=false -> run fails before touching data.
  * The schedule ships STOPPED. Turn it on in the UI when you trust the pipeline.
  * max_concurrent_runs=1 in dagster.yaml.
"""
from pathlib import Path

import dagster as dg
import duckdb
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets
from dagster_dlt import DagsterDltResource, DagsterDltTranslator, dlt_assets
from dagster_dlt.translator import DltResourceTranslatorData

from . import config
from .ingest import make_pipeline, placeholder_source


def guard(context: dg.AssetExecutionContext) -> None:
    if not config.pipeline_enabled():
        raise dg.Failure(
            description="KILL SWITCH: PIPELINE_ENABLED is not 'true'. Refusing to run.",
            allow_retries=False,
        )
    context.log.info("Kill switch check passed.")


# ---------- 1. Ingest (dlt -> DuckLake raw.*) ----------
class RawTranslator(DagsterDltTranslator):
    """Name dlt assets raw/<table> so dbt sources can depend on them cleanly."""

    def get_asset_spec(self, data: DltResourceTranslatorData) -> dg.AssetSpec:
        spec = super().get_asset_spec(data)
        return spec.replace_attributes(
            key=dg.AssetKey([config.RAW_SCHEMA, data.resource.name]),
            deps=[],
            group_name="ingest",
        )


@dlt_assets(
    dlt_source=placeholder_source(),
    dlt_pipeline=make_pipeline(),
    name="placeholder_ingest",
    dagster_dlt_translator=RawTranslator(),
)
def ingest_assets(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
    guard(context)
    yield from dlt.run(context=context)


# ---------- 2. Transform (dbt -> DuckLake staging/marts) ----------
DBT_DIR = Path(__file__).resolve().parent.parent / "dbt_project"
dbt_project = DbtProject(project_dir=DBT_DIR, profiles_dir=DBT_DIR)
dbt_project.prepare_if_dev()


@dbt_assets(manifest=dbt_project.manifest_path)
def dbt_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    guard(context)
    yield from dbt.cli(["build"], context=context).stream()


# ---------- 3. Publish (DuckLake marts -> Postgres analytics.public) ----------
@dg.asset(
    group_name="serve",
    deps=[dg.AssetKey(["marts", name]) for name in config.PUBLISHED_MARTS],
    description="Copies marts into Postgres so Evidence and Metabase can read them natively.",
)
def published_marts(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    guard(context)
    con = duckdb.connect()
    try:
        con.execute("LOAD ducklake; LOAD postgres;")
        con.execute(
            f"ATTACH 'ducklake:postgres:{config.pg_libpq(config.LAKE_CATALOG_DB)}' "
            f"AS {config.LAKE_NAME} (METADATA_SCHEMA '{config.LAKE_METADATA_SCHEMA}', READ_ONLY)"
        )
        con.execute(f"ATTACH '{config.pg_libpq(config.ANALYTICS_DB)}' AS serving (TYPE postgres)")
        # Check BEFORE replacing anything: never overwrite good serving data with an empty mart.
        counts = {
            name: con.execute(f"SELECT count(*) FROM {config.LAKE_NAME}.marts.{name}").fetchone()[0]
            for name in config.PUBLISHED_MARTS
        }
        if any(c == 0 for c in counts.values()):
            raise dg.Failure(description=f"Refusing to publish empty mart(s): {counts}")
        for name in config.PUBLISHED_MARTS:
            con.execute(f"DROP TABLE IF EXISTS serving.public.{name}")
            con.execute(
                f"CREATE TABLE serving.public.{name} AS "
                f"SELECT * FROM {config.LAKE_NAME}.marts.{name}"
            )
            context.log.info(f"Published {name}: {counts[name]} rows")
        return dg.MaterializeResult(metadata={f"rows_{k}": v for k, v in counts.items()})
    finally:
        con.close()


# ---------- Schedule: ships STOPPED ----------
everything = dg.define_asset_job("full_refresh", selection=dg.AssetSelection.all())

daily = dg.ScheduleDefinition(
    job=everything,
    cron_schedule="0 6 * * *",
    execution_timezone="America/Chicago",
    default_status=dg.DefaultScheduleStatus.STOPPED,
)

defs = dg.Definitions(
    assets=[ingest_assets, dbt_models, published_marts],
    jobs=[everything],
    schedules=[daily],
    resources={
        "dlt": DagsterDltResource(),
        "dbt": DbtCliResource(project_dir=dbt_project),
    },
)
