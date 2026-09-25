"""dlt source: JSONPlaceholder (free, no auth) -> DuckLake raw schema.

Swap this for a real source later. dlt's rest_api source handles pagination,
retries, and schema evolution; JSONPlaceholder just keeps the demo credential-free.
"""
import os

import dlt
from dlt.destinations.impl.ducklake.configuration import DuckLakeCredentials
from dlt.sources.rest_api import rest_api_source

from . import config


def placeholder_source():
    return rest_api_source(
        {
            "client": {
                "base_url": "https://jsonplaceholder.typicode.com/",
                "paginator": "single_page",
            },
            "resource_defaults": {"write_disposition": "replace"},
            "resources": [
                {"name": "users", "primary_key": "id", "endpoint": {"path": "users"}},
                {"name": "posts", "primary_key": "id", "endpoint": {"path": "posts"}},
                {"name": "comments", "primary_key": "id", "endpoint": {"path": "comments"}},
            ],
        },
        name="placeholder",
    )


def lake_destination():
    return dlt.destinations.ducklake(
        credentials=DuckLakeCredentials(
            ducklake_name=config.LAKE_NAME,
            metadata_schema=config.LAKE_METADATA_SCHEMA,
            catalog=config.pg_url(config.LAKE_CATALOG_DB),
            storage=config.LAKE_DATA_PATH,
        )
    )


def make_pipeline():
    return dlt.pipeline(
        pipeline_name="placeholder_to_lake",
        destination=lake_destination(),
        dataset_name=config.RAW_SCHEMA,
        pipelines_dir=os.getenv("DLT_PIPELINES_DIR", "/data/dlt_pipelines"),
    )
