---
layout: post
title: Building a data lake on Microsoft Azure.
date: 2023-03-01 05:18:00
description: Building and deploying a data lake on Azure infrastructure.
related_posts: false
tags: bigdata azure data-engineering scala python
featured: false
toc: 
  beginning: true
---

# Introduction
## Pre-requisite reading
In order to fully understand or follow along with the article, I recommend reading some of the documents, articles and other links I have included in this section. If you have already worked on the AWS services I have listed below, you can skip this section.


## Infrastructure as Code (IaC)
All of the Azure cloud resources discussed can be created manually via the Azure Portal.

In a production deployment, that is seldom the case. We typically use an Infrastructure as Code deployment to manage resources. Azure provides native support for IaC via the [Azure Resource Manager](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview) model. 

Azure supports other third-party platforms such as Terraform. To illustrate resource creation in this article, I will use Terraform examples for resource creation.

## What is a Data Lake?
> A data lake is a centralized repository that ingests and stores large volumes of data in its original form. The data can then be processed and used as a basis for a variety of analytic needs. Due to its open, scalable architecture, a data lake can accommodate all types of data from any source, from structured (database tables, Excel sheets) to semi-structured (XML files, webpages) to unstructured (images, audio files, tweets), all without sacrificing fidelity. The data files are typically stored in staged zones—raw, cleansed, and curated—so that different types of users may use the data in its various forms to meet their needs. Data lakes provide core data consistency across a variety of applications, powering big data analytics, machine learning, predictive analytics, and other forms of intelligent action.
>
> <cite>--Microsoft Azure Documentation.</cite>

# Use cases
It is cost effective and performant to build a Data Lake when the data volume is over a certain threshold. The threshold is usually in the tens of GBs of data per day and continues to accumulate over time. If the data volume is less than that, it would be quicker and cheaper to build a traditional data warehouse or other solutions.

As we saw above, a Data Lake is a centralized repository which stores all of the structured and unstructured data. This means that this data is available to anyone in an organization (with the relevant permissions). This could be - Data Analysts, Data Scientists, Data Engineers, Business Analysts, Product Managers, Finance or any other function. This offers a single source of truth of the data and each sub-function or department within an organization can choose to use the data as they see fit, with their own tooling for data access, analytics and visualization.


# Data sources
## Azure Storage Account
## Synapse
## Eventhubs

# Permissions

# Destination

# Design decisions and trade-offs
## Compute
## Storage
## Analytics
## Security
## Costs and Scaling up/down
## Alerting and Monitoring

# Conclusion