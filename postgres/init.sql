-- One Postgres, four jobs. Separate databases keep blast radius small.
CREATE DATABASE dagster;       -- Dagster run/event storage
CREATE DATABASE lake_catalog;  -- DuckLake catalog (table metadata, snapshots)
CREATE DATABASE analytics;     -- Serving layer that Evidence + Metabase read
CREATE DATABASE metabase;      -- Metabase's own application DB
