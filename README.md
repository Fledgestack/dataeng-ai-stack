# 7-repo open-source data stack (homelab edition)

`dlt → DuckLake (DuckDB) → dbt-core → Dagster → Postgres serving → Evidence + Metabase`

## Run it

```bash
make init        # creates .env with a random password
make up          # builds + starts (first build ~5-10 min)
make run         # ingest -> transform -> publish, once
make evidence-refresh
```

| UI | URL |
|---|---|
| Dagster (lineage, runs) | http://localhost:3000 |
| Evidence (BI as code) | http://localhost:3001 |
| Metabase (self-serve) | http://localhost:3002 → add a PostgreSQL database: host `postgres`, db `analytics`, user/password from `.env` |

## Kill switches

| Command | Effect |
|---|---|
| `make kill` | Stops Dagster daemon + webserver. Schedules and in-flight runs die. BI stays up. |
| `make pause` | `PIPELINE_ENABLED=false`. Containers stay up; every asset fails at the guard before touching data. |
| Schedule | Ships **STOPPED**. Turn it on in the Dagster UI only when you trust it. |
| Concurrency | `max_concurrent_runs: 1` in `dagster.yaml`. |
| Publish guard | `published_marts` refuses to overwrite serving tables with an empty mart. |

## What was verified before shipping

- All Python pins resolve together on Python 3.12 (`pip install` clean).
- Dagster loads the full asset graph: `raw/*` → `staging/*` → `marts/fct_user_engagement` → `published_marts`, schedule defaults to STOPPED.
- dbt parses with zero deprecation warnings; the models + 10 data tests pass (14/14) against dlt-normalized data in DuckDB.

**Not verified in the sandbox (no Docker/GPU there):** the DuckLake-on-Postgres attach at runtime, the Evidence build, and the containers themselves. First real run is yours. If DuckLake attach fails, check that `metadata_schema` is `lake` in both `stack/config.py` and `dbt_project/profiles.yml`.

## Swap points

- **Transform:** want SQLMesh instead of dbt? Replace `dbt_project/` and the `dbt_models` asset. Same owner (Fivetran) either way since 2025/2026.
- **Source:** replace `stack/ingest.py` with any dlt source. JSONPlaceholder is just a credential-free demo.
- **Evidence:** the OSS framework now lives on the template's `legacy` branch; main moved to the commercial Evidence Studio CLI. Pinned by commit in `evidence/Dockerfile`.

## Ports used
3000-3002, 5433 (Postgres, localhost only). Agent harness uses different ports, so both stacks can run side by side.
