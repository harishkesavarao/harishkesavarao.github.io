---
layout: page
title: Open Source Contributions
description: Active contributions to Apache Airflow, Delta Lake — focused on data infrastructure, observability, and provider tooling.
importance: 2
category: side-projects
---

I contribute to open-source projects in the data engineering and AI/ML infrastructure space. Contributions span provider tooling, observability improvements, and platform compatibility fixes.


#### Apache Airflow
##### Databricks provider, Google provider, Snowflake provider

[DatabricksPartitionSensor](https://github.com/apache/airflow/pull/30980) — authored and merged; enables partition-level sensing on Databricks tables for dependency management in Airflow DAGs
[DatabricksSQLSensor](https://github.com/apache/airflow/pull/30477) — authored and merged; SQL-based sensing for Databricks workflows
[Fix malformed URI](https://github.com/apache/airflow/pull/20509)† — Snowflake Connector
Google BigQuery & PubSub provider [unit test fixes](https://github.com/apache/airflow/pull/22213)†
Google Sheets & Simple HTTP [unit test fixes](https://github.com/apache/airflow/pull/22104)† 

Note: contributions linked above marked with † were made under @harishkrao


#### Delta Lake
##### delta-io/delta

Improved error observability in SnapshotManager.getLogSegmentForVersion — enhanced diagnostics for version resolution failures, making debugging significantly faster for users hitting log segment errors ([PR](https://github.com/delta-io/delta/pull/5329) approved, pending merge)
