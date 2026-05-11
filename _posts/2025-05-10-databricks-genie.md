---
layout: post
title: "A Practitioner's Journey with Databricks AI/BI Genie"
date: 2025-05-10
tags: [databricks, genie, ai-bi, llm, unity-catalog, data-mesh, natural-language-analytics]
description: >
  What building a natural language analytics layer over production customer 
  data actually looks like — two months, 25 tables, a structured pilot, 
  and a direct review from the Databricks team.
---

This post speaks about what it takes to  actually build a [Databricks Genie](https://www.databricks.com/blog/aibi-genie-now-generally-available) Space over production customer data in a data mesh architecture — from first configuration to a stable, production-ready Space used by business teams across Customer Support 
and Customer Success.

The timeline: two months from initial setup to opening access beyond a structured technical pilot. The audience: non-technical users who needed answers from data but had no SQL expertise.

We were among the early adopters of Genie at the time of this work. The Databricks team reviewed our Space configuration directly and provided feedback — a process that both validated the approach and 
surfaced refinements that would have taken longer to discover independently.

---

## The starting point: data mesh as an advantage

Prior to building a Genie space, the data foundation was already in good shape. This was achieved by years of careful data curation:

- The tables exposed to Genie were part of a data mesh architecture
- Table, column names and metadata were created by close collaboration with (and feedback from) business users: they must be meaningful to business consumers — not just to data engineers.
- Layers of data with a defined purpose, with the top-most layer containing metrics for consumers
- Acronyms and metric definitions were documented at the point of data product creation, which meant that Genie could readily learn from it.

Table metadata was one of the most important factors in Genie accuracy. <a href="https://docs.databricks.com/aws/en/genie/best-practices" target="_blank">Databricks' documentation</a> is explicit about this: quality table and column descriptions in Unity Catalog are critical for Genie accuracy. Well-documented, simplified datasets improve Genie's ability to answer data questions accurately. 

> A well-annotated data product is not just good data governance practice. It is pre-training for the Genie Space.

Additonally, the tables connected had different levels of granularity: dimension tables, fact tables, and wide metric tables at different aggregation levels. Transformations or table/column renamings were not needed before connecting the tables to Genie — the cleaning and standardisation had already been done as part of the data product implementation.

---

## Setup: what we actually did vs. what the documentation recommends

Databricks' documentation recommends starting with five or fewer tables. We connected all 25 — the maximum available at the time (the limit is now 30). This was intentional, since we needed the data layers to present a complete picture to our users.

**A word of caution:** The consequence of this approach is instructive, and it is the central finding of this post: starting at maximum table count meant that the configuration work required to achieve reliable accuracy was significantly higher from the outset. The documentation's recommendation to start small is not conservative caution — it reflects how the system actually behaves as complexity scales. More on this in the accuracy section.

The UI setup itself was straightforward.

### Initial configuration

**A substantial glossary in text instructions.** We added approximately 20 acronyms with explicit business context definitions. This prevents the possibility of a concept/acronym/term that appears in column names or user questions to be misinterpreted. 

Databricks recommends writing clear, specific text instructions rather than vague guidance, and this applies to glossary entries too. For example, "ARR means Annual Recurring Revenue" is insufficient. "ARR refers to Annual Recurring Revenue in USD at the account level, calculated as of the last day of the reporting period" gives Genie the context to apply the term correctly across different question types.

**Explicit join specifications.** Join hints in the instructions ensures that Genie uses the correct tables, the correct join keys, and in the correct direction. This had a substantial positive effect — it prevented Genie from constructing its own joins between tables that happened to share column names but should not be joined for a given question type. There were also scenarios where each business area needed its corresponding join condition which will be incorrect for a different business area. Combining the join instruction with an explicit text instruction to use that specific join was helpful.

**15–20 example SQL queries.** They function as few-shot examples that Genie uses when generating SQL for similar questions. The selection criteria that mattered most: 

- Cover the most frequent question patterns first
- Match the question phrasing to what users actually type
- Include at least one example for every join path and aggregation grain users are likely to need

Databricks' guidance prioritises SQL expressions and example SQL over text instructions — in practice, the example SQL queries were the highest-leverage input to accuracy.

**Benchmark questions.** Genie does not use benchmark questions to improve its context. They are evaluation tools, not training inputs. Their value is in detecting regressions — every time a new table or instruction was added, the benchmark suite was run to verify that existing accurate responses had not degraded. Overall, the aim was to ensure a benchmark of 85-90% as the criteria before exposing the space to decision makers.

---

## The pilot structure: two months to production

Getting to a state worth showing users took approximately one month of iterative configuration. The process was not linear — it was a cycle of:
- Asking questions
- Examining the generated SQL
- Identifying failure modes
- Updating instructions or example queries
- Re-running benchmarks.

After reaching a reasonably accurate baseline, we ran a structured technical pilot with five users before opening the space up to a broader business audience. The pilot users were technical enough to identify incorrect SQL and distinguish between a wrong answer and an ambiguous question — which matters, because not every inaccurate response is a Genie problem. Some reflect ambiguity in the question itself, and the right response is a clarification instruction, not more example SQL. Follow-up question prompts had to be added to the instructions.

The general feedback was:
- Tables with richer metadata
- Wider pre-joined metric-dimension structures
- Pre-joined examples as instructions performed better regardless of the underlying data type
- The data model mattered more than the domain.

Databricks recommends business users for testing and setting the expectation that their role is to help refine the space. **The structured pilot with technical users first was an additional layer before this — and it proved worthwhile. Business users encounter a better-calibrated Space; technical pilot users catch the failure modes that business users would simply interpret as the system not working.**

---

## The accuracy journey: non-linear and instructive

### Early accuracy

When the Genie space was initially setup, responses were more accurate than expected for cut-and-dried question patterns. When Genie could not answer a question, it said so explicitly — requesting more context or stating that it lacked the information to respond. 

This transparency is a feature worth calling out: 
**A well-configured Genie Space fails gracefully. It does not silently return wrong results.**

### Accuracy at scale

As the question breadth increased or the datasets' count increased, three failure modes emerged:

**Wrong metric values.** Genie would select the correct table but the wrong column — typically because multiple columns represented similar concepts at different grains or under different business definitions, and the instructions did not distinguish between them clearly enough.

**Wrong joins.** With 25 tables available, Genie would sometimes join tables that shared column names but should not have been joined for a given question. The explicit join specifications in the instructions substantially reduced this, but it remained a failure mode for question patterns not covered by example SQL.

**Confident but wrong aggregations.** The most operationally dangerous failure mode — results that were plausible and well-formatted but aggregated at the wrong grain. A question intended to surface account-level metrics being answered at event level, for example. The results were not obviously wrong, which made this harder to catch without systematic benchmark testing.

### Recovery: the iterative approach

The response to each failure mode:

| Problem | Solution |
| ------- | -------- |
| Wrong metric values | Added explicit instructions specifying which column to use for each of the concepts/areas, with context on when each applies|
| Wrong joins | Added text instructions for joins, although example SQLs were more effective combined with these; added example SQLs | 
| Wrong aggregation grain | Added grain-specific example SQLs and text instructions defining the default grain for each metric category |

The benchmark questions helped evaluate if each change was improving or degrading the model's accuracy. Without systematic measurement across the entire dataset and business area(s), there was no reliable way to know whether a fix for one failure mode was introducing a regression elsewhere.

> At lower complexity, the prompts in Genie were sufficient to guide the agent towards acceptable accuracy. As question breadth and table count grew, the instructions/prompts had not covered the questions and datasets. 

---

## Best practices from Databricks' documentation

**Build on well-annotated tables before opening the Genie UI.** Writing descriptive column metadata at data product creation time.

**Prioritise SQL expressions and example SQL over text instructions.** 
- Databricks recommends using SQL expressions to define business semantics like metric definitions or filters, and example SQLs to teach Genie how to handle ambiguous questions from users. 
- The example SQL queries were the most direct way in influecing the model's thinking towards accuracy. 
- Text instructions were necessary for the glossary and global domain rules, as an augmentation to the  example queries.

**Write clear, specific text instructions.** 
The documentation recommends avoiding vague instructions — instead of "Ask clarification questions when asked about sales," write "When users ask about sales metrics without specifying product name or sales channel, ask: To proceed with sales analysis, specify your product name and sales channel."

**Use benchmarks to measure, not to train.** 
Benchmarks allow you to run a collection of test questions and use the responses to measure Genie's accuracy — Genie does not use benchmark questions or example SQL to improve Genie's context. Treating benchmarks as the regression test suite for every instruction change was the practice that made iterative improvement data-driven rather than speculative.

**Conduct structured user testing before broad rollout.** 
Databricks recommends setting expectations with pilot users that their role is to help refine the space, and asking them to focus testing on the specific topic and questions the space is designed to answer. 
The technical pilot step before business user access was beneficial.

**Prompt Genie to ask clarification questions explicitly.** 
Adding structured clarification instructions for:
- Defining branching conditions based on user inputs
- Identifying and asking for missing details that typically are needed for a well formulated response

Alonsgide this, adding example clarification questions proved helpful.

These instructions reduced the rate of ambiguous responses for question types where users did not provide specifics such as time ranges or segment filters. Feedback loops of clarifications help users gain more confidence in the model and improves response accuracy.

---

## Finishing note

Databricks AI/BI Genie is a system you build incrementally — validating, and expanding scope as the prompt matures. The accuracy is largely determined by the quality of the underlying data and metadata. It is also determined by how thoroughly the business area/domain is covered with example SQLs, explicit join specifications, and instructions.

---

## Further reading

**[Databricks AI/BI Demo Library](https://www.databricks.com/resources/demos/library?q=ai%2Fbi)**

**[What are Compound AI Systems? — Databricks Blog](https://www.databricks.com/blog/what-are-compound-ai-systems)**

**[The Shift from Models to Compound AI Systems — BAIR Blog](https://bair.berkeley.edu/blog/2024/02/18/compound-ai-systems/)**