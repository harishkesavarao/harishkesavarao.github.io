---
layout: page
title: Open Source Contributions
description: Contributions to OSS projects
importance: 2
category: side-projects
---

Periodically, I make Open Source contributions in the way of features and doing code reviews.

**Major contributions:**

Over the past 2 years, I have contributed to [Apache Airflow](https://airflow.apache.org/) (used for workflow automation and scheduling that can be used to author and manage data pipelines)

**Databricks SQL sensor:**
[Pull request](https://github.com/apache/airflow/pull/30477/files) and [code](https://github.com/apache/airflow/blob/main/airflow/providers/databricks/sensors/databricks_sql.py).

Use the DatabricksSqlSensor to run the sensor for a table accessible via a Databricks SQL warehouse or interactive cluster.

[Official Apache Airflow Documentation, contributed as part of the above PR.](https://airflow.apache.org/docs/apache-airflow-providers-databricks/stable/operators/sql.html#databrickssqlsensor)


**Databricks Partition sensor:**
[Pull request](https://github.com/apache/airflow/pull/30980/files) and [code](https://github.com/apache/airflow/blob/main/airflow/providers/databricks/sensors/databricks_partition.py).

Use the DatabricksSqlOperator to execute SQL on a [Databricks SQL warehouse](https://docs.databricks.com/sql/admin/sql-endpoints.html) or a [Databricks cluster](https://docs.databricks.com/clusters/index.html).

[Official Apache Airflow Documentation, contributed as part of the above PR.](https://airflow.apache.org/docs/apache-airflow-providers-databricks/stable/operators/sql.html#databrickspartitionsensor)

**Other contributions:**

- [Google BigQuery and PubSub provider unit test fixes.](https://github.com/apache/airflow/pull/22213)
- [Google Sheets and Simple HTTP unit test fixes.](https://github.com/apache/airflow/pull/22104)

*Note: Above contributions made using my other GitHub handle [@harishkrao](https://github.com/harishkrao)*