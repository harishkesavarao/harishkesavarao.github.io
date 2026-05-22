---
layout: post
title: "Building a Governed Data Lakehouse"
date: 2025-08-04
tags: [data-architecture, data-lakehouse, data-governance, data-engineering, data-mesh, data-contracts, data-quality, delta-lake, data-platform]
description: >
  A first-hand account of building a governed, standardised data lakehouse 
  across an organisation — what the architecture decisions actually look like, 
  why governance has to be structural rather than aspirational, and what 
  happens when you skip it.
---

## Introduction

Most data teams building a data lakehouse think of governance, schema conformity, transactional integrity, or versioning as an afterthought. By the time they get to it, there are already three definitions of "active customer," two pipelines implementing logic for flavours of the same use case, and several dashboards reading from the same source but producing different numbers for the same metric — quietly eroding trust in the entire data platform.

The cost of getting data governance wrong is not abstract. It is data swamps, compliance exposure, and AI systems that hallucinate because the data they were trained on was never reliable to begin with. The decisions you make in the early phase of a greenfield lakehouse project have a lasting impact on the data platform. I learned this by having lived through the consequences of both getting it right early and retrofitting it later. This post is an account of what building a governed lakehouse actually looks like in practice.

---

## Why do organizations need a data lakehouse?

It is important to understand what a data lakehouse is and what problems does it solve.

Earlier, organisations managed their data lifecycle through three separate systems:
	 - a data warehouse for structured analytics
	 - a data lake for raw and unstructured data
	 - separate ML platforms for model development
	 - the BI layer on top of the above systems
	 
Each system had its own access control, audit trail and governance framework. This resulted in an architecture where moving data between systems was quite cumbersome along with the added overhead of maintaining multiple copies of the same data, in different formats, with different freshness guarantees, compounding over time.

The lakehouse pattern combines all of this and aims to simplify the data architecture. It combines the flexibility and cost-effectiveness of a data lake with the reliability and query performance of a data warehouse — in a single, open-format and unified architecture. Structured, semi-structured, unstructured, and streaming data: all of these coexist in the same platform. Analytics, ML, and AI workloads run against the same underlying data. And there is one governance layer for all of it.

This is technically possible due to the underlying storage format layer. Traditional data lakes lacked ACID transaction support — failed jobs could corrupt files, multiple pipelines writing concurrently could compromise data integrity, and schema enforcement was absent by default. Modern open table formats like Delta Lake and Apache Iceberg provide ACID guarantees, schema enforcement, time travel, and audit history on top of Parquet — bringing data warehouse reliability to the flexibility of object storage. That is the foundation everything else is built on.

However, having a reliable storage format does not automatically mean it is a governed lakehouse.

---

## What is "well-governed" in the context of a data lakehouse?

A well-governed lakehouse:

- contains data that can be trusted
- is secure
- is discoverable
- is reliable.

Governance is baked into the architecture from the beginning, not retrofitted afterward.

It also means the organisation is at some stage of a data maturity curve. In the early stages, the focus is on historical reporting — structured data, SQL queries, precanned dashboards. As maturity increases, teams add streaming data, ML workloads, predictive analytics. At the most mature end, organisations build AI systems that reason over their own data — RAG pipelines, agents, natural language interfaces. Each stage of that curve makes higher demands on the governance layer beneath it.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/data-ai-maturity-curve.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>


Let us walk through how that looks like in practice.

---

## Layered architecture with clear contracts

The Bronze / Silver / Gold pattern — Medallion architecture — is widely adopted but inconsistently implemented. The layers only work if each one has a clear contract: what data enters, in what form, with what guarantees, and what happens when those guarantees are violated.

Bronze is raw. Exactly as received, append-only, with ingestion metadata. Silver is cleaned, conformed, and deduplicated. Gold is aggregated and optimised for consumption.

The contract between Silver and Gold is where most teams are vague — and where most governance failures originate. If a Gold table is rebuilt from a Silver table that changed its schema without notice, every downstream consumer breaks silently. Clear contracts mean documented grain, documented SLAs, and a defined breaking-change policy. Not in a wiki that nobody reads — in the table metadata, enforced by the pipeline.

One thing I would tell someone starting this from scratch: the layer boundaries feel like overhead in week one. By month six, they are the only thing keeping the platform coherent as the number of producers and consumers multiplies.

---

## Naming things consistently across a large team

This sounds trivial. It is not.

When ten teams are building pipelines independently, naming conventions diverge fast. A column called `customer_id` in one domain turns out to be a different entity from `customer_id` in another — same name, 
different grain, different update cadence. Joins that look correct produce wrong results. Data quality checks pass. Reports diverge. Nobody knows why until someone traces it by hand.

The conventions that mattered most in practice: domain-prefixed table names, consistent use of surrogate versus natural keys across the platform, standardised date column naming (`created_at`, `updated_at`, 
`effective_from`, `effective_to`), and agreed abbreviation rules for column names in YAML-defined data products.

The last one is underrated. When data products are declared declaratively — schema, column descriptions, grain, SLAs — naming consistency becomes enforceable rather than advisory. Teams cannot easily drift from a standard that is codified in the data product specification.

---

## Domain ownership

A central data team that owns every table in the lakehouse does not scale. Data mesh principles exist for a reason: the teams closest to the data understand it best, and ownership should reflect that. In practice, domain ownership means the team producing the data is responsible for its quality, its schema evolution, and its SLAs. The platform team provides the guardrails — Unity Catalog access policies, schema validation, lineage tracking — but does not own the data itself.

The failure mode is when domain ownership becomes domain isolation: teams build pipelines that do not conform to platform standards, use different naming conventions, and cannot be joined reliably across domains. Platform guardrails prevent this. Ownership without guardrails is just decentralised chaos.

What it looks like in practice when a team takes genuine responsibility for their data products: they write column descriptions that explain business meaning, not just data type. They define the grain explicitly. They version their schemas. They own their SLA and are paged when they miss it. The difference between a team that owns their data and a team that merely produces it is visible in the quality of the metadata.

---

## Data contracts

A data contract is the explicit agreement between a data producer and its consumers. It covers four things: schema, grain, SLAs, and the breaking-change policy.

**Schema:** what columns exist, their types, and which are nullable.

**Grain:** what one row represents — one event, one account per day, one transaction. This is the most commonly undocumented and most commonly violated property. Grain errors are dangerous because the results they produce are not obviously wrong — they are plausible, well-formatted, and incorrect.

**SLA:** when the data is available and how fresh it is guaranteed to be.

**Breaking-change policy:** what constitutes a breaking change, how much notice consumers receive, and what the migration path looks like.

The specific failure mode that convinced me contracts were not optional: 
a producer table had a column silently retyped from integer to string during a routine pipeline refactor. The downstream Gold table schema validation caught it six hours later, after three dashboards had already served incorrect aggregations to business stakeholders. Tracing the root cause took two engineers most of a day. The fix took twenty minutes. A contract with a breaking-change policy would have prevented the silent retype from reaching downstream without a version bump and consumer notification.

---

## Governance and access

Data classification is the foundation. Before you can apply access controls, you need to know what you have: PII, financial data, internal-only metrics, publicly referenceable aggregates. Unity Catalog's tagging system handles this if used consistently — and "if used consistently" is doing significant work in that sentence.

RBAC (role-based) and ABAC (attribute-based) access controls operate at different granularities. RBAC is table-level and schema-level. ABAC is row-level and column-level — masking a PII column for one role 
while exposing it to another. Both are necessary. RBAC alone leaves too much exposed; ABAC alone is difficult to audit.

PII handling is not just masking. It is retention policies, audit logging of who accessed what, and ensuring that PII does not leak through derived columns or aggregations that are re-identifiable. The last one is the most commonly missed: a count-by-postcode table is not PII, but a count-by-postcode-by-age-bracket with small cell sizes can re-identify individuals. Governance in regulated environments has to 
account for derived sensitivity, not just source sensitivity.

---

## Making data findable and traceable

Lineage is the one capability organisations invest in last and regret most.

When a number in a board-level dashboard is wrong, the first question is always "where does this come from?" Without lineage, that question takes days to answer — often involving archaeology through pipeline 
code, Airflow DAG histories, and Slack message searches. With lineage, it is a query.

What a catalogue is actually for — versus what people think it is for: 
most teams treat the data catalogue as a documentation project. A place to write descriptions and tag tables. That is the wrong framing. A catalogue is a runtime artefact. It reflects the live state of the data platform: what tables exist, what they contain, who owns them, when they were last updated, and how they relate to each other. Documentation that lives separately from the pipeline inevitably falls behind the pipeline. Descriptions written at data product creation time — as part of the schema definition — stay current because they are versioned alongside the schema.

Tagging and classification tiers work best when they are mandatory at data product registration time, not optional at consumption time. A sensitivity tag added when a table is first defined is almost always 
more accurate than one added retroactively when a compliance audit surfaces it.

---

## Data observability

Data observability covers five properties: freshness, volume, distribution, schema, and lineage.

**Freshness:** is the data as recent as the SLA promises?

**Volume:** are row counts within expected bounds? A pipeline that 
silently drops 40% of records is a governance failure, not just an 
engineering one.

**Distribution:** are column value distributions stable? A shift in 
the distribution of a key dimension is often the first signal of 
an upstream data quality issue — before any explicit data quality 
check fires.

**Schema:** did the schema change without a corresponding contract update?

**Lineage:** can you trace a value in a Gold table back to its source system?

The ownership question matters more than the tooling. A team that owns their data product owns the observability signals for that product. They set the expected volume bounds. They define what "freshness" means for their SLA. They are paged when the distribution shifts. Observability tooling without ownership is just dashboards nobody acts on.

How we built observability into pipelines without making it someone's full-time job: by making it declarative. Expected row count ranges, null rate thresholds, and distribution bounds are defined in the data product specification alongside the schema. The pipeline validates against them at each layer boundary. Violations block promotion from Bronze to Silver. This is not a separate observability system — it is the pipeline enforcing the contract at runtime.

---

## Semantic layer

One governed definition per metric. This is the principle that most data teams agree with and almost none implement consistently.

A semantic layer sits between the physical data model and the consumer — whether that consumer is a BI tool, an analyst running SQL, or an AI agent generating queries. It defines what "revenue" means, what "active user" means, what time zone "today" refers to. One definition, one place, applied consistently.

Without it, different teams build their own definitions in their own tools. The organisation ends up with five different revenue numbers depending on which dashboard you open. This is not a data quality problem — it is a governance problem. The data is correct; the definitions are inconsistent.

The semantic layer is also where the connection to AI readiness becomes concrete. An AI agent generating SQL against your lakehouse will use whatever metric definitions it can infer from column names and table descriptions. If those definitions are inconsistent, the agent produces inconsistent results. A governed semantic layer is not optional for AI-powered analytics — it is the prerequisite.

---

## AI-readiness

This is where governance stops being an internal engineering concern and becomes a product requirement. An LLM querying your lakehouse — whether through a natural language query interface, a RAG pipeline, or a custom agent — depends entirely on the quality of your metadata. Column descriptions that say "flag" or "id" are useless to a language model. Column descriptions that say "binary indicator set to 1 when the account has had an active subscription within the last 30 days" are genuinely useful. The difference between a Genie Space that returns accurate results and one that hallucinates is largely determined by the quality of the column-level annotations in Unity Catalog.

AI-readiness means descriptions are written for a language model, not a data engineer. It means embeddings exist for columns and tables so that semantic search over the data catalogue works. It means agent-accessible metadata — what tables exist, what they contain, how they relate — is current and accurate, which is only possible if it is maintained at data product definition time rather than retroactively.

A lakehouse without this is not AI-ready. Point an LLM at undocumented tables with opaque column names and you will get confident, plausible, wrong answers. The data quality problem that used to surface as a 
wrong number in a dashboard now surfaces as a confident hallucination in an AI system that business users trust more, not less, than the dashboard it replaced.

---

## Walking through one example end to end

Follow a single `transaction` entity from source through to the reporting layer to see how naming, contracts, lineage, and quality checks touch the same record at different points.

**Bronze:** the transaction arrives from the source system exactly as received — raw JSON, appended to the Bronze table with an `ingested_at` timestamp. No transformation. The schema is documented; the grain is one event per row.

**Silver:** the transaction is cleaned, typed, deduplicated, and conformed to the platform naming convention. `txn_id`, `account_sk`, `transaction_amount_usd`, `transaction_ts`. The Silver contract specifies grain (one transaction per `txn_id`), nullable columns, and a freshness SLA of T+4 hours. A row count check validates that Silver contains within 1% of the expected Bronze volume. A null check validates that `account_sk` is never null.

**Gold:** the transaction is aggregated to the account-day grain — `daily_account_revenue`, `transaction_count`, `avg_transaction_value`. The Gold contract specifies that "revenue" means `sum(transaction_amount_usd)` where `transaction_status = 'settled'`. This definition is registered in the semantic layer. Every downstream consumer — BI tool, analyst SQL query, AI agent — uses the same definition.

**Lineage:** a Unity Catalog lineage trace from the Gold metric back to Bronze is available. When a reporting discrepancy surfaces, the trace takes minutes, not days.

This is what governance built into the architecture looks like, as opposed to governance bolted on afterward.

---

## What ungoverned looks like

It is useful to name the failure modes directly:

- **Definition drift** — the same metric calculated differently by  different teams, diverging silently over months
- **Undocumented PII** — personal data in columns that are not tagged, not masked, and not audited; a compliance exposure that nobody knows about until it matters
- **Broken lineage** — a pipeline refactored six months ago but the lineage graph never updated, so the dependency map is wrong
- **Dashboard divergence** — two dashboards showing different numbers for the same metric, both technically correct by their own definitions, neither trustworthy
- **Small-file proliferation** — hundreds of thousands of tiny Parquet files accumulating in a Bronze table with no compaction policy, degrading query performance progressively until someone notices

These are not edge cases. They are the default state of an ungoverned lakehouse at scale.

---

## What I would tell someone starting this from scratch

Governance done early feels like overhead. It pays back quickly.

The things I would do on day one that I did not do on day one: define the data contract structure before any team writes their first pipeline. Agree on the naming conventions before any table is created. Make 
column descriptions mandatory at schema definition time, not optional at documentation time. Instrument lineage from the start, not after the first incident that requires it.

The hardest part of building a governed lakehouse is not the tooling. It is the organisational discipline to maintain standards as the number of teams, tables, and consumers grows. Platform guardrails help, but they do not substitute for teams that genuinely own their data products.

Governance is not a project with an end date. It is an engineering discipline — built into the architecture, maintained by the teams that own the data, and enforced by the platform. The moment you treat it 
as a compliance checkbox, you have already lost. The moment you treat it as a product requirement, you have a lakehouse that can actually support the AI applications your organisation is building on top of it.
