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

## Key topics

There are four topics we cover here:

- Assessing a data project's requirement
- Trade-offs 
- Suggestions for data modeling
- Implementation: design aspects and choices

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

**Before implementing, assess the trade-offs between:**

- Architectural complexity vs. Analytical Flexibility
- Platform standardization vs. Usability
- Cost vs. Performance vs. Accuracy (some teams are okay with approximations)
- Time of delivery vs. Feature lists

---

## Some suggestions during data modeling

**Build partnerships:** With upstream data producers and downstream data consumers. Get frequent and early feedback during the design phase.

**Intentional modeling:** Understand the key entities. Progress from a logical model to a physical model with clear objectives for each model type.

**Understand the data:** Understand attributes, profile the data, and map attributes to business taxonomy. This also helps in understanding the quality of data.

**Consider the bigger picture:** Where does this model fit in the overall architecture? Can existing components be reused? Can this model complement rather than duplicate other models?

**Build data quality into the design:** Profile the data and include data quality as part of the design process. This step also helps decide the kinds of checks needed to be built to ensure the data is correct and reliable. Get feedback from all user types in this phase.

**Data contracts** Define specifications, service level agreements, semantics, data quality and metadata for discoverability.

---

## Implementation: design aspects and choices

Think of these design aspects and choices:

**Build vs. extend:** Does the requirement need a solution from scratch, or can an existing solution be enhanced or extended? Extending is almost always faster and cheaper when feasible. The temptation to build from scratch is worth resisting until it is clearly necessary.

**Data sources:** 
- Are you using the right data source? What are your data contracts with the owners? 
- Have we assessed data quality and is it acceptable by you and your users? If not, what are the alternatives? Are there other sources? 
- If the source changes or there is a change in the data schema or other metadata, how is that change communicated to downstream consumers? How does the data contract manage it? 

**Last-mile consumption:** 
- What use cases exist today, and what other use cases could be solved by the same model? 
- How are users going to consume the data? 
- Materialization vs. views. Normalization vs. dimensional model (wide table for reports). 

**Costs:** Data retention requirements, performance vs. compute and storage costs. Some use cases do not need sub-second latency as long as the data is of good quality while for others, accuracy matters as much as on-time data delivery. Choices need to be taken accordingly. Additionally, the cost justification should also be quantified from the business value that the data provides to users - such as enabling them make better and faster decisions or allowing them to see data points which were previously not available.

**ETL strategy:** Incremental vs. full load. Change capture mechanisms.

**Batch vs. real-time:** These largely depend on: 
- latency
- volume
- cost
- complexity
- consistency

**Optimization:** Maintenance (optimize commands, vacuuming), partitioning, clustering, read efficiency, write efficiency. Optimization is a continuous exercise, requiring measurements of job runtimes, read and write delays and last-mile data refresh performance. Based on the numbers from these measurements, appropriate optimization techniques could be used. 

**Communication strategy:** Early feedback, dependency management with upstream and downstream users, and user adoption are part of this process. Frequent feedback loops increase user adoption. Frequent, clear and direct communication allow users to be prepared of upcoming changes in data or other artifacts generated out of the pipelines.

---

## Three principles to carry forward

**Customer first:** Build only if you know the data will be used. Get early and constant feedback. 

**It is a continuous journey:** Data architecture is iterative. Do not let perfect be the enemy of good. Ship things fast, learn from them, and improve.

**Your design will be around:** Ensure that your design stands the test of time, scalability, and extensibility.

---

## Further reading

- *Designing Data-Intensive Applications* by Martin Kleppmann
- *The Data Warehouse Toolkit*, 3rd Edition by Kimball Group
- *The Architecture Design Stamina Hypothesis* by Martin Fowler
