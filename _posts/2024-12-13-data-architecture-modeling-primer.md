---
layout: post
title: "Data Architecture and Modeling — A Primer"
date: 2024-12-13
tags: [data-architecture, data-modeling, data-engineering, data-governance, dimensional-modeling]
description: >
  A practitioner's primer on data architecture and modeling detailing how to assess
  requirements, think about design trade-offs, and implement solutions that
  remain relevant over time.
---

Data Architecture and Data Modeling are two expansive topics. It is not
possible to cover the breadth and depth of these over a single post. However, this post highlights the topics I find being most useful in practice, particularly amongst data engineering teams which are building or evolving a data platform.

---

## Key themes

There are three themes we cover here:

- Assessing a requirement and most importantly, before building anything
- Thinking about data architecture and data modeling as a discipline, not just a technical task
- Implementing the best possible solution given real-world constraints (this is where we discuss trade-offs)

---

## Assessing a requirement

Before beginning a data architecture project, it is worth spending time understanding a project's/initiative's requirements. There are two useful lenses for assessing any requirement:

**From the user or customer perspective:**
- What is the overall requirement?
- Why is it a requirement now — what has changed recently?
- Who are the core users? What are their objectives?

**From the engineering team's perspective:**
- What are we trying to do — and can we state it clearly? If yes, can we also break it down into smaller, manageable pieces?
- What is the business impact if we get it right, and what are the consequences if we get it wrong?
- Does a solution already exist that could be extended or reused? Are other teams working on something similar?

---

## Think trade-offs

There are two ways of looking at a requirement:

**Tactical approach:** take on each task, focus on the immediate requirement and meet short-term goals.

**Strategic software engineering** — consider future implications, maintain a big-picture perspective and identify likely areas of future change.

The situation and timeline of the project decide which approach is right. In the early phases of a project, tactical development is often
the right call. As the system matures and more teams begin using it, the cost of tactical decisions compounds.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/martin-fowler-design-stamina-hypothesis.png" class="img-fluid rounded z-depth-1" zoomable=true caption="The design stamina hypothesis. Source: Martin Fowler"%}
    </div>
</div>

Martin Fowler's Design Stamina Hypothesis captures this well.

**Before implementing, assess the trade-offs:**

- Complexity vs. Analytical Flexibility
- Standardization vs. Usability
- Data Quality vs. Usability
- Cost vs. Performance
- Time vs. Features

These tensions are real and recur in every data project. Making them explicit
before implementation prevents decisions from being made implicitly, usually
under time pressure, in ways that are hard to reverse.

---

## Some suggestions during data modeling

**Build partnerships:** With upstream data producers and downstream data consumers. Get frequent and early feedback during the design phase. A model that is technically correct but does not serve the people who use it is not a good model.

**Intentional modeling:** Understand the key entities before touching a tool. Move deliberately from a logical model to a physical model rather than jumping
straight to implementation.

**Understand the data:** Understand attributes, profile the data, and map attributes to business impact. The data will surprise you; profiling surfaces those surprises before they become production issues.

**Consider the bigger picture:** Where does this model fit in the overall architecture? Can existing components be reused? Can this model complement rather than duplicate other models?

**Build data quality into the design:** Work with users to set expectations upfront. Profile the data and establish data contracts as part of the design process, not as an afterthought.

**Data contracts** Define specifications, service level agreements, and metadata for discoverability. A data contract is the explicit agreement between a producer and its consumers. Without it, consumers build on assumptions that will eventually be violated.

---

## Implementation — design aspects and choices

When moving from design to implementation, a set of specific decisions need to be made. These are not one-time decisions. They come up repeatedly across
every data product.

**Build vs. extend:** Does the requirement need a solution from scratch, or can an existing solution be enhanced or extended? Extending is almost always faster and cheaper when feasible. The temptation to build from scratch is worth resisting until it is clearly necessary.

**Data sources:** Are you using the right data source? Are there alternative sources? If the source changes, how is that change communicated to downstream consumers? Source stability is often underestimated as a design concern.

**Last-mile consumption:** What use cases exist today, and what other use cases could be solved by the same model? How are users going to consume the data? Materialization vs. views. Normalization vs. dimensional model (wide table for reports). The consumption pattern should drive the physical model design, not the other way around.

**Cost:** Data retention requirements and compute and storage costs. These are engineering decisions with real budget consequences. Retention policies in particular are often decided too late, after data has already accumulated at a cost nobody budgeted for.

**ETL strategy:** — incremental vs. full load. Change capture mechanisms. An incremental strategy is almost always preferable at scale but introduces complexity around change detection and idempotency. The trade-off needs to be made consciously.

**Batch vs. real-time:** Five dimensions to evaluate: latency, volume, cost, complexity, and consistency. Real-time processing is not always better. For many analytical use cases, batch processing with a well-defined SLA is simpler, cheaper, and more reliable.

**Optimization:** Maintenance (optimize commands, vacuuming), partitioning, clustering, read efficiency, write efficiency. Optimization decisions made at design time are much cheaper than those retrofitted after a system is in production.

**Communication strategy:** Early feedback, dependency management upstream and downstream, and adoption. A technically excellent model that nobody uses or that breaks downstream consumers on every schema change is not a success. Communication and dependency management are engineering concerns, not soft skills.

---

## Three principles to carry forward

**Customer first:** Build only if you know the data will be used. Get early and constant feedback. The cost of building something that nobody uses is not just the initial engineering time. It is the ongoing maintenance cost of a system that adds no value.

**It is a continuous journey:** Data architecture is iterative. Do not let perfect be the enemy of good. Ship things, learn from them, and improve. The goal is not to get the design right the first time; it is to design in a way that makes iteration possible.

**Your design will be around:** Ensure that your design stands the test of time, scalability, and extensibility. The decisions made in week one follow a system for years. Design with that in mind.

---

## Further reading

- *Designing Data-Intensive Applications* by Martin Kleppmann
- *The Data Warehouse Toolkit*, 3rd Edition by Kimball Group
- *The Architecture Design Stamina Hypothesis* by Martin Fowler
