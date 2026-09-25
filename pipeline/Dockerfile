FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DAGSTER_HOME=/opt/dagster/home

WORKDIR /opt/dagster/app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Pre-install DuckDB extensions at build time so runs never download code at runtime.
RUN python -c "import duckdb; c=duckdb.connect(); c.execute('INSTALL ducklake'); c.execute('INSTALL postgres')"

COPY dagster.yaml ${DAGSTER_HOME}/dagster.yaml
COPY workspace.yaml .
COPY stack ./stack
COPY dbt_project ./dbt_project

# Build the dbt manifest at image build time (parse needs no DB connection).
RUN cd dbt_project && dbt parse --profiles-dir .

EXPOSE 3000
