"""Single source of truth for connection settings. Everything reads env vars."""
import os

PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_USER = os.getenv("POSTGRES_USER", "stack")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
LAKE_CATALOG_DB = os.getenv("LAKE_CATALOG_DB", "lake_catalog")
ANALYTICS_DB = os.getenv("ANALYTICS_DB", "analytics")
LAKE_DATA_PATH = os.getenv("LAKE_DATA_PATH", "/data/lake/")

# DuckLake names. dlt and dbt MUST agree on these or dbt attaches an empty lake.
LAKE_NAME = "lake"          # ATTACH alias
LAKE_METADATA_SCHEMA = "lake"  # schema inside the Postgres catalog DB
RAW_SCHEMA = "raw"          # where dlt lands data

# Marts that get published to the Postgres serving layer for BI tools.
PUBLISHED_MARTS = ["fct_user_engagement"]


def pipeline_enabled() -> bool:
    """The in-code kill switch. Anything other than 'true' stops every run."""
    return os.getenv("PIPELINE_ENABLED", "true").strip().lower() == "true"


def pg_libpq(dbname: str) -> str:
    """libpq-style connection string, the format DuckDB's postgres/ducklake extensions expect."""
    return f"dbname={dbname} host={PG_HOST} port={PG_PORT} user={PG_USER} password={PG_PASSWORD}"


def pg_url(dbname: str) -> str:
    return f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{dbname}"
