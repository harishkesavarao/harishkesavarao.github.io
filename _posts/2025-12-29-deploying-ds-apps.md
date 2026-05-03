---
layout: post
title: Deploying Data Science applications - from a Data Engineer's perspective
date: 2025-12-29 08:18:00
description: Thoughts and observations from a recent journey of deploying a Data Science pilot application
related_posts: false
tags: bigdata data-engineering hive airflow python data-science
featured: true
toc: 
  beginning: true
---

Recently, I had the opportunity to work with Data Scientists to understand, partner and scale a Semantic Search and Theming application. 

It was an interesting journey for several reasons: 
- Learning Data Science concepts, techniques (something I had always wanted to do)
- Understanding Search and Theming from a business value standpoint
- How a Data Scientist's perspective of features and scalability is both same and different (more on this below)?

### Learning Data Science concepts

Over the past few years, a Data Engineer's primary (who is your customer and what are you building for them?) set of use cases has slowly evolved from pure analytics (for technical and business decision makers) to a combination of analytics (for Product Managers, decision makers) and machine learning models (for Data Scientists, data analysts). 

This requires a Data Engineer to gain more context about what they are building. For instance:

- What does semantic search do? 
- What are the different kinds of Machine Learning models? What are they used for?
- What is the difference between analytics and machine learning applications?
- Which techniques in machine learning are more suited for the kinds of problems being solved by Data Scientists? 

This also requires a Data Engineer to read more about some of the fundamentals of these topics, because a data scientist is probably well acquainted with these and to be able to discuss and solve problems with them, a Data Engineer needs to: 

- Understand the basics of Data Science
- Know how to educate Data Scientists with the nuances of Data Engineering as it pertains to their use cases
- Agree on trade-offs and roadmap priorities with their Data Scientists

### Understanding business value

At the end of a specific initiative, it is always important for both Data Engineers and Data Scientists to understand: 

- Who their customers are? 
- What are they looking for? 
- What problems can the DE + DS team solve for them? 

Complicated problems do not necessarily need a deep, elaborate solution. It might just as well need a closer look at the problem to understand, refine and arrive at a clear problem statement and then break it down to: 

- Smaller use cases
- Roadmap items
- Deliverable priorities

This also includes getting frequent and early feedback from both Data Scientists and business users alike.

### Features and scalability

Typically, when developing data pipelines for any use case, one might want to consider: 

1.  Ingesting data at an agreed upon latency
2. Transforming data to meet the use cases' needs
3. Loading (writing) data into the appropriate storage with considerations for read and write optimizations. In other words, perform ETL or ELT (swap steps 2 and 3). 
4. Additionally, implement data quality checks at several points along the pipeline to alert users about data anomalies.

Now, when it comes to explorative analyses for Data Science, Data Scientists typically use iPython notebooks to quickly iterate upon their experiments or ideas. They use numpy or pandas (for Python stacks or R in some cases). They want to view results quickly for a small sample of data. This might result in:

- Smaller and duplicated temporary tables or views being created
- Multiple print/display/show statements being used
- Repeated code blocks with variations for experiments

From a Data Engineering perspective, it will be sub-optimal to convert this notebook into a scheduled workload, running across a wide range of data for dates or other attributes. From my experience over the past few months, a few items to look out for:

- Numpy or pandas uses a single node for compute. As data volume scales, it requires parallelization using Spark, for instance. These code blocks need to be refactored into using Spark dataframes and functions
- Each time a print/display/show statement is executed, data gets collected to the Spark driver. This needs to be removed or converted to logging statements. 
    - Logging statements should also display pre-calculated dataframe results or perform minimal actions on dataframes to prevent redundant or expensive actions
- Statistics used for data profiling should be optional for large loads
- API calls should contain retries,backoff strategies and checks should be implemented to validate results returned from them
- Data chunking should be implemented as data volumes grow - either by date or other appropriate attributes
- Choose an appropriate compute type and node size

Data Engineers work with Data Scientists to go over several iterations of modifications and/or optimizations to ensure that the iPython notebook used for development becomes a scalable, reusable and extensible data pipeline.
