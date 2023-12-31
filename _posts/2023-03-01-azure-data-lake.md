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

- [Storage account overview.](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview)

- [IaC on Azure.](https://learn.microsoft.com/en-us/devops/deliver/what-is-infrastructure-as-code)

- [Azure Resource Manager.](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview)

- [Azure Service Principals.](https://learn.microsoft.com/en-us/entra/identity-platform/app-objects-and-service-principals?tabs=browser)

- [Azure role-based access control (RBAC).](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-steps)

## Infrastructure as Code (IaC)
All of the Azure cloud resources discussed can be created manually via the Azure Portal.

In a production deployment, that is seldom the case. We typically use an Infrastructure as Code deployment to manage resources. Azure provides native support for IaC via the [Azure Resource Manager](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview) model. 

Azure supports other third-party platforms such as Terraform. To illustrate resource creation in this article, I will use Terraform examples for resource creation.

## What is a Data Lake?
> A data lake is a centralized repository that ingests and stores large volumes of data in its original form. The data can then be processed and used as a basis for a variety of analytic needs. Due to its open, scalable architecture, a data lake can accommodate all types of data from any source, from structured (database tables, Excel sheets) to semi-structured (XML files, webpages) to unstructured (images, audio files, tweets), all without sacrificing fidelity. The data files are typically stored in staged zones—raw, cleansed, and curated—so that different types of users may use the data in its various forms to meet their needs. Data lakes provide core data consistency across a variety of applications, powering big data analytics, machine learning, predictive analytics, and other forms of intelligent action.
>
>
> <cite>-- Microsoft Azure Documentation.</cite>

# Use cases
It is cost effective and performant to build a Data Lake when the data volume is over a certain threshold. The threshold is usually in the tens of GBs of data per day and continues to accumulate over time. If the data volume is less than that, it would be quicker and cheaper to build a traditional data warehouse or other solutions.

As we saw above, a Data Lake is a centralized repository which stores all of the structured and unstructured data. This means that this data is available to anyone in an organization (with the relevant permissions). This could be - Data Analysts, Data Scientists, Data Engineers, Business Analysts, Product Managers, Finance or any other function. This offers a single source of truth of the data and each sub-function or department within an organization can choose to use the data as they see fit, with their own tooling for data access, analytics and visualization.


# Data sources
From what I have seen, most data sources in Azure fall under one of two types: Azure Storage Account and Eventhubs (streaming). We will discuss the following topics for these two data sources:

- How are we authenticating to these sources before ingesting data from them?
- What are the most efficient methods to ingest data from the two source types?

We will not discuss the destination storage in this section. We will do it in the design decisions section.

## Azure Storage Account
[Related Azure Doc.](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview)

There are many types of storage accounts. For the purpose of this article, we will discuss Standard general-purpose v2, which supports the Azure Blob Storage (and Data Lake Storage) service. 

### Authorization
Options to authenticate to a storage account in Azure. 

You can always define the following authentication keys using the Azure Portal, Azure CLI or other manual/UI means. For a production system, it is important to think of automated deployment of resources using IaC and via [CI/CD.](https://en.wikipedia.org/wiki/CI/CD) In this context, Azure recommends using what is called as an Application and an associated Service Principal. 

_Excerpt from Azure Docs below:_

> Automated tools that use Azure services should always have restricted permissions. Instead of having applications sign in as a fully privileged user, Azure offers service principals.
>
> An Azure service principal is an identity created for use with applications, hosted services, and automated tools to access Azure resources. This access is restricted by the roles assigned to the service principal, giving you control over which resources can be accessed and at which level. For security reasons, it's always recommended to use service principals with automated tools rather than allowing them to log in with a user identity.
>
> Microsoft recommends using Service Principals to authenticate access to resources as much as possible. To understand how to create Service Principals, how they are related to an Application, Tenant and resources, please read the sections on Service Principal and Azure RBAC.
>
>
> <cite>-- Microsoft Azure Documentation.</cite>

Setting up access to an Azure Storage Account via an Azure Service Principal is explained [here.](https://learn.microsoft.com/en-us/dynamics365/customer-insights/data/connect-service-principal)

**[Shared Key (WARNING: has full access to the storage account config and data)](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-keys-manage?tabs=azure-portal)**: a shared key is passed with every request to the storage account. The shared key is created along with each storage account and can be used for authorization. Since it contains full access to a storage account, it is discouraged to use this as a standard authorization option.

If you choose to use the shared key to access a Storage Account, an associated [connection string](https://learn.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string?toc=/azure/storage/blobs/toc.json&bc=/azure/storage/blobs/breadcrumb/toc.json) needs to be generated alongside the shared key. 

**Delegated access with shared access signatures (SAS):**
> A shared access signature (SAS) enables you to grant limited access to containers and blobs in your storage account. When you create a SAS, you specify its constraints, including which Azure Storage resources a client is allowed to access, what permissions they have on those resources, and how long the SAS is valid.
>
>
> <cite>-- Microsoft Azure Documentation.</cite>

### Ingestion

**Data Migration**

**Event handling**
https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-event-overview

**Event Queue for Storage Account:**

## Eventhubs

### Authorization

### Ingestion

# Design decisions and trade-offs
## Compute

https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-decision-tree

## Storage / Azure Storage Account

**Security**

**Data Protection**

**Access tiers, lifecycle management**

**Performance, scalability**

**Cost planning, optimization**

## Analytics
## Security
## Costs and Scaling up/down
## Alerting and Monitoring


# Conclusion