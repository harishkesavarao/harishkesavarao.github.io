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

It also means the organisation is at some stage of a data maturity curve.

1. In the early stages, the focus is on historical reporting — structured data with batch loads, SQL queries, precanned dashboards.
2. As maturity increases, teams add streaming data, ML workloads, predictive analytics.
3. At the most mature end, organisations build AI systems that learn from their data and its surrounding metadata — RAG pipelines, agents, natural language interfaces.

Each stage of that curve makes higher demands on the governance layer beneath it.


<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/data-ai-maturity-curve.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Image courtesy: Databricks"%}
    </div>
</div>

Let us walk through how that looks like in practice.

---

## Layered architecture with clear data contracts

The Medallion architecture — the Bronze / Silver / Gold pattern is widely adopted across the industry.

- Bronze is raw data, which is stored exactly as it is received, is append-only, and contains ingestion metadata.
- Silver is cleaned, conformed, and deduplicated data.
- Gold is aggregated and optimised data, ready for consumption.

However, the architecture is not effective if it is inconsistently implemented. The layers work only with a clear contract definition for each layer:

- what data enters
- in what form
- with what guarantees
  - what happens when those guarantees are violated.

This is typically effective when enforced via a combination of process and system checks.

In practice, the contract between the Silver and the Gold layers is where ambiguity typically sets in — and also where most governance failures can occur. Teams often debate upon what goes into which layer and what the contracts for the layers are. It is important to achieve a clear consensus early on and stick to it. If a Gold table is rebuilt from a Silver table whose schema was changed without notice, every downstream consumer breaks. Clear contracts mean documented grain, documented SLAs, and a defined breaking-change policy (most importantly involving Standard Operating Procedures around communication to all stakeholders).

The layer boundaries might feel like overhead at the beginning. As the data platform matures, they ensure that the platform is consistently governed as the number of producers and consumers multiplies.

---

## Global naming convention

When several teams are building pipelines independently, naming conventions diverge over time. A column called `customer_id` in one domain turns out to be a different entity from `customer_id` in another — same name, different grain, different update cadence. Joins that look correct produce wrong results. Data quality checks pass and produce data inconsistency or corruption downstream. Reports diverge.

The conventions that mattered most in practice: domain-prefixed table names, consistent use of surrogate versus natural keys across the platform, standardised date column naming (`created_at`, `updated_at`, 
`effective_from`, `effective_to`), and agreed abbreviation rules for column names in data products.

When data products are declared declaratively — schema, column descriptions, grain, SLAs — naming consistency becomes enforceable rather than advisory. Teams cannot easily drift from a standard that is codified in the data product specification.

On a slightly different note, such problems are usually discovered by Data Quality checks at several points in the pipeline. If a team does not have such checks in place, these problems are reported by customers or business users, which results in delayed problem discovery, wrong decisions being made due to incorrect data and more such probelms. Identifying the source of the problem becomes a tedious task as well, since without the Data Quality checks, it is hard to know where the problem is originating.

---

## Domain ownership

It is not scalable to have a central data team own every table in the lakehouse. Data mesh principles guide such scenarios: the teams closest to the data understand it best, and should own not just the data, but the entire data lifecycle and its governance. In practice, this concept of domain ownership means the team producing the data is responsible for its quality, its schema evolution, and its SLAs. The platform team provides the guardrails — Unity Catalog access policies, schema validation, lineage tracking and other tooling, but does not own the data itself.

The other important guardrail from the platform is standardization. Enforcing standards as part of the platform prevents teams from building pipelines that do not conform to agreed contracts, using different naming conventions, and build tables with fields which cannot be joined reliably across domains. 

What it looks like in practice when a team is responsible for their data products:
- they write column descriptions that explain business meaning, not just data type.
- they define the grain explicitly.
- they version their schemas.
- they own their SLA and are paged when they miss it.

The difference between a team that owns their data and a team that merely produces it is visible in the quality of the metadata.

---

## Data contracts

A data contract is the explicit agreement between a data producer and its consumers. It mainly covers four things: schema, grain, SLAs, and the breaking-change policy.

**Schema:** what columns exist, their types, and which are nullable.

**Grain:** what one row represents — one event, one account per day, one transaction. This is the most commonly undocumented and most commonly violated property.

**SLA:** when the data is available and how fresh it is guaranteed to be.

**Breaking-change policy:** what constitutes a breaking change, how much notice consumers receive, and what the migration path looks like.

An example scenario: 
a producer table's column type was recently changed from integer to string during a routine pipeline refactor. The downstream Gold table schema data quality check caught it six hours later, after three dashboards had already served incorrect aggregations to business stakeholders. Tracing the root cause took two engineers almost a day. The fix took twenty minutes thereafter.
A contract with a breaking-change policy would have prevented the type change from reaching downstream without a version increment and consumer notification.

---

## Governance and access

Data classification precedes access control decisions. Before you can apply access controls, you need to know if the incoming data contains: PII, user generated content, financial data, internal-only metrics, publicly referenceable aggregates. For instance, Databricks Unity Catalog's tagging system handles this if used consistently.

Access controls in most cloud platforms include RBAC (role-based) and ABAC (attribute-based) access controls which provide controls at different granularities. RBAC is table-level and schema-level. ABAC is row-level and column-level. For example, they could be used to mask a PII column for one role while exposing it to another.

PII handling includes masking, but it also includes retention policies, audit logging of who accessed what, and ensuring that PII does not leak through derived columns or aggregations. Governance in regulated environments has to account for derived sensitivity, not just source sensitivity.

---

## Making data findable and traceable

Lineage is the one capability organisations invest in last and struggle to get it right for a long time later.

When a number in a board-level dashboard is wrong, the first question is always "where does this come from?" Without lineage, that question takes days to answer without end-to-end data flow lineage. With lineage, it is a simple query of the tables storing the lineage relationships.

What a catalogue is actually for — versus what people think it is for: 
most teams treat the data catalogue as a documentation project. A place to write descriptions and tag tables. That is the wrong framing. A catalogue is a runtime artefact. It reflects the live state of the data platform: what tables exist, what they contain, who owns them, when they were last updated, and how they relate to each other. Documentation that lives separately from the pipeline inevitably falls behind the pipeline. Descriptions written at data product creation time — as part of the schema definition — stay current because they are versioned alongside the schema.

Tagging and classification tiers work best when they are mandatory at data product registration time, not optional at consumption time. A sensitivity tag added when a table is first defined is almost always 
more accurate than one added retroactively when a compliance audit surfaces it.

---

## Data observability

Data observability covers five properties: freshness, volume, distribution, schema, and lineage.

**Freshness:** is the data as recent as defined in the SLA?

**Volume:** are row counts within expected bounds? Are we recording the % of deviation from the average row counts for the past 30 days?

**Distribution:** are column value distributions stable? A shift in the distribution of a key dimension is often the first signal of an upstream data quality issue

**Schema:** did the schema change without a corresponding contract update?

**Lineage:** can you trace a value in a Gold table back to its source system?

The ownership question matters more than the tooling. A team that owns their data product owns the observability signals for that product.

- They set the expected volume numbers.
- They define what "freshness" means for their SLA.
- They are paged when the distribution shifts.

By making observability declarative, we built it into pipelines without making it another task to be performed later. Expected row count ranges, null rate thresholds, and distribution are defined in the data product specification alongside the schema. The pipeline validates against them at each layer. Violations block promotion from Bronze to Silver. This is not a separate observability system — it is the pipeline enforcing the contract at runtime.

---

## Semantic layer

One governed definition per metric. This is the principle that most data teams agree with consistently.

A semantic layer sits between the physical data model and the consumer — whether that consumer is a BI tool, an analyst running SQL, or an AI agent generating queries. It defines what "revenue" means, what "active user" means, what time zone "today" refers to. One definition, one place, applied consistently.

Without it, different teams build their own definitions in their own tools. The organisation ends up with five different revenue numbers depending on which dashboard you open. This is not a data quality problem — it is a governance problem. The data is correct; the definitions are inconsistent.

The semantic layer is also where the connection to AI readiness becomes concrete. An AI agent generating SQL against your lakehouse will use whatever metric definitions it can infer from column names and table descriptions. If those definitions are inconsistent, the agent produces inconsistent results.

---

## AI-readiness

An LLM querying your lakehouse — whether through a natural language query interface, a RAG pipeline, or a custom agent — depends entirely on the quality of your metadata. Column descriptions that say "flag" or "id" are useless to a language model. Column descriptions that say "binary indicator set to 1 when the account has had an active subscription within the last 30 days" are genuinely useful. The difference between a Genie Space that returns accurate results and one that hallucinates is largely determined by the quality of the column-level annotations in Unity Catalog.

AI-readiness means:
- descriptions are written for a language model, not a data engineer.
- embeddings exist for columns and tables so that semantic search over the data catalogue works.
- agent-accessible metadata — what tables exist, what they contain, how they relate — is current and accurate. This is possible if it is maintained at data product definition time rather than retroactively.

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

## Ungoverned data platforms

These are some problems arise in a data platform without governance:

- **Definition drift** — the same metric calculated differently by  different teams, diverging silently over months
- **Undocumented PII** — personal data in columns that are not tagged, not masked, and not audited; a compliance exposure that nobody knows about until it matters
- **Broken lineage** — a pipeline refactored six months ago but the lineage graph never updated, so the dependency map is wrong
- **Dashboard divergence** — two dashboards showing different numbers for the same metric, both technically correct by their own definitions, neither trustworthy
- **Small-file proliferation** — hundreds of thousands of tiny Parquet files accumulating in a Bronze table with no compaction policy, degrading query performance progressively until someone notices

---

## Conclusion

Governance done early feels like overhead. It pays in the long term.

The things I would do on day one that I did not do on day one: define the data contract structure before any team writes their first pipeline. Agree on the naming conventions before any table is created. Make 
column descriptions mandatory at schema definition time, not optional at documentation time. Instrument lineage from the start.

The hardest part of building a governed lakehouse is not the tooling. It is the organisational discipline to maintain standards as the number of teams, tables, and consumers grows. Platform guardrails help, but they do not substitute for teams that genuinely own their data products.

Governance is an engineering discipline — built into the architecture, maintained by the teams that own the data, and enforced by the platform.
