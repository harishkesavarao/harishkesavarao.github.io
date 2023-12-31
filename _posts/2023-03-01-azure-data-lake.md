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
In order to fully understand or follow along with the article, I recommend reading some of the documents, articles and other links I have included in this section. If you have already worked on the Azure services I have listed below, you can skip this section.

1. [Storage account overview.](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview)
2. [IaC on Azure.](https://learn.microsoft.com/en-us/devops/deliver/what-is-infrastructure-as-code)
3. [Azure Resource Manager.](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview)
4. [Azure Service Principals.](https://learn.microsoft.com/en-us/entra/identity-platform/app-objects-and-service-principals?tabs=browser)
5. [Azure role-based access control (RBAC).](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-steps)
6. [Azure Event Hubs.](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-about)
7. [Production considerations for Structured Streaming.](https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/production)
8. [Azure Monitor.](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/monitor-azure-resource#monitoring-data)
9. [Azure Monitor Alerts](https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-types)
10. [Lifecycle Management Policies for Azure Storage Account.](https://learn.microsoft.com/en-us/azure/storage/blobs/lifecycle-management-overview)


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

```terraform
resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_storage_account" "example" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    environment = "staging"
  }
}
```
<cite> -- Terraform Docs.</cite>

### Authentication and authorization
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

More information on creating a SAS token [here](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-user-delegation-sas-create-cli). The article explains using a security principal (an user, group or a Service Principal) to first assign the `Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey` action to the security principal or via an RBAC such as `Storage Blob Data Contributor` and then use the permissions to then create an user delegated SAS using it.

```terraform
resource "azurerm_resource_group" "example" {
  name     = "resourceGroupName"
  location = "West Europe"
}

resource "azurerm_storage_account" "example" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    environment = "staging"
  }
}

data "azurerm_storage_account_sas" "example" {
  connection_string = azurerm_storage_account.example.primary_connection_string
  https_only        = true
  signed_version    = "2017-07-29"

  resource_types {
    service   = true
    container = false
    object    = false
  }

  services {
    blob  = true
    queue = false
    table = false
    file  = false
  }

  start  = "2018-03-21T00:00:00Z"
  expiry = "2020-03-21T00:00:00Z"

  permissions {
    read    = true
    write   = true
    delete  = false
    list    = false
    add     = true
    create  = true
    update  = false
    process = false
    tag     = false
    filter  = false
  }
}

output "sas_url_query_string" {
  value = data.azurerm_storage_account_sas.example.sas
}
```
<cite> -- Terraform Docs.</cite>


## Azure Event Hubs
[Related Azure doc.](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-about)

> Azure Event Hubs is a cloud native data streaming service that can stream millions of events per second, with low latency, from any source to any destination. Event Hubs is compatible with Apache Kafka, and it enables you to run existing Kafka workloads without any code changes.
>
> <cite>-- Microsoft Azure Documentation.</cite>

Eventhubs allows ingesting streaming data to a data lake. We will confine our discussion to receiving data, setting up authorization and a few other basics in this section. Ingestion data will be discussed in the Ingestion section for Event Hubs. 

```terraform
resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_eventhub_namespace" "example" {
  name                = "acceptanceTestEventHubNamespace"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "Standard"
  capacity            = 1

  tags = {
    environment = "Production"
  }
}

resource "azurerm_eventhub" "example" {
  name                = "acceptanceTestEventHub"
  namespace_name      = azurerm_eventhub_namespace.example.name
  resource_group_name = azurerm_resource_group.example.name
  partition_count     = 2
  message_retention   = 1
}
```
<cite> -- Terraform Docs.</cite>

### Authentication and authorization
The authorization mechanism for event hubs is similar to the SAS token we discussed for Azure Storage Account, with the only difference being, we can define authorization policies associated with each event hubs topic (you can define a SAS token for an eventhubs namespace or as well, but I prefer to do it a event hubs topic level to keep it more granular). The policy defines the level of access for the SAS token.

[Authentication](https://learn.microsoft.com/en-us/azure/event-hubs/authenticate-shared-access-signature) and [authorization](https://learn.microsoft.com/en-us/azure/event-hubs/authorize-access-shared-access-signature) using a shared access signature. 

You can generate SAS authorization policies and tokens using the Security Principal method described above in the Storage Account's Authorization section.

```terraform
resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_eventhub_namespace" "example" {
  name                = "acceptanceTestEventHubNamespace"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "Basic"
  capacity            = 2

  tags = {
    environment = "Production"
  }
}

resource "azurerm_eventhub" "example" {
  name                = "acceptanceTestEventHub"
  namespace_name      = azurerm_eventhub_namespace.example.name
  resource_group_name = azurerm_resource_group.example.name
  partition_count     = 2
  message_retention   = 2
}

resource "azurerm_eventhub_authorization_rule" "example" {
  name                = "navi"
  namespace_name      = azurerm_eventhub_namespace.example.name
  eventhub_name       = azurerm_eventhub.example.name
  resource_group_name = azurerm_resource_group.example.name
  listen              = true
  send                = false
  manage              = false
}
```
<cite> -- Terraform Docs.</cite>

# Ingestion
So far, we have discussed data sources and associated authorization mechanisms. Now, we will discuss methods to ingest data from the different data sources using the configured authorization. A few design questions related to ingestion:

- How frequently do you need to ingest - batch, streaming?
- What is your expected throughput when ingesting data? Can you data lake tolerate some delay at the benefit of reduced cost?
- Do you need to deploy infrastructure related to ingestion? What kinds of resources? Are specific authorization mechanisms needed for these?

## Azure Storage Account

**Data Migration** 

When it comes to ingesting data into a Data Lake, the first level of ingestion usually involves the copying of raw data. In other words, data is ingestd as-is from the source and no data transformations take place. This simplifies things for the first-level ingestion, where you do not have to build an ETL pipeline to copy/move data.

The Azure CLI `az storage blob copy` [command](https://learn.microsoft.com/en-us/cli/azure/storage/blob/copy?view=azure-cli-latest) is helpful in performing such batch copy operations from the source Azure Storage Account to the destination (Data Lake) Azure Storage Account. The [authentication and authorization mechanisms](#authentication-and-authorization) we discussed during the Azure Storage Account data sources can be used when running the command.

**Event handling**

Instead of scheduling a batch copy, we can ingest data using an event-driven mechanism. [Azure Storage Accounts can be configured to send certain (specified via a filter) events to Azure Event Grid](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-event-overview). Event Grid then delivers these events to applications listening to it.

[Read here](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-event-overview#filtering-events) about filtering events to be sent to the Event Grid. [Some caveats](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-event-overview#practices-for-consuming-events) to watch when using this option for ingestion. 

[Azure Queue Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-event-overview#practices-for-consuming-events) is one of the applications which can be configured to listen to Azure Event Grid. Your client application can then read queue messages from Azure Queue Storage. A Python code sample is available [here](https://learn.microsoft.com/en-us/azure/storage/queues/storage-quickstart-queues-python?tabs=passwordless%2Croles-azure-portal%2Cenvironment-variable-windows%2Csign-in-visual-studio-code). 

```terraform
resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_storage_account" "example" {
  name                     = "exampleasa"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    environment = "staging"
  }
}

resource "azurerm_storage_queue" "example" {
  name                 = "example-astq"
  storage_account_name = azurerm_storage_account.example.name
}

resource "azurerm_eventgrid_event_subscription" "example" {
  name  = "example-aees"
  scope = azurerm_resource_group.example.id

  storage_queue_endpoint {
    storage_account_id = azurerm_storage_account.example.id
    queue_name         = azurerm_storage_queue.example.name
  }
}

resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_storage_account" "example" {
  name                     = "examplestorageacc"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_queue" "example" {
  name                 = "mysamplequeue"
  storage_account_name = azurerm_storage_account.example.name
}

```
<cite> -- Terraform Docs.</cite>

## Azure Event Hubs

**Azure Event Hubs for Kafka**

[Event Hubs data can be consumed using a Kafka Consumer](https://learn.microsoft.com/en-us/azure/event-hubs/azure-event-hubs-kafka-overview). The authentication mechanism is the same, and I prefer to use the SAS connection string created along with the authorization rule/policy.

Usually, given larger volumes for a big data lake, we can configure [Spark Structured Streaming for Kafka](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-kafka-spark-tutorial#read-from-event-hubs-for-kafka) and consume events from Azure Event Hub. More information on configuring Kafka (bootstrap servers, security protocol, sasl mechanism, sasl jaas config etc.) and other settings [here](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-quickstart-kafka-enabled-event-hubs?tabs=connection-string#send-and-receive-messages-with-kafka-in-event-hubs).

**Event handling**

The same mechanism for event handling for Azure Storage Account applies to Event Hubs as well. And not just for Event Hubs, there are a [number of Azure services](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-event-overview#the-event-model) which can send data to Azure Event Grid. 

Once the [required permissions](#authentication-and-authorization-1) are configured for Event Hubs, the topic can send data to the Event Grid.

# Design decisions and trade-offs

## Compute

Azure provides comprehensive documentation on different compute types. Based on your use case, you can follow the [flowchart here](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-decision-tree) and choose a compute type for your workloads.


## Storage / Azure Storage Account

[Security recommendations for Blog Storage.](https://learn.microsoft.com/en-us/azure/storage/blobs/security-recommendations#loggingmonitoring) - specifically data protection, networking and logging/monitoring sections.

If you are storing sensitive data in your destination Azure Storage Account for the Data Lake, it is all the more important to setup [logging and monitoring](https://learn.microsoft.com/en-us/azure/storage/blobs/monitor-blob-storage?tabs=azure-portal) for the Storage Account. 

**Access tiers, lifecycle management**

[Reading for this section.](https://learn.microsoft.com/en-us/azure/storage/blobs/lifecycle-management-overview)

Azure Storage Management Policy.

```terraform
resource "azurerm_resource_group" "example" {
  name     = "resourceGroupName"
  location = "West Europe"
}

resource "azurerm_storage_account" "example" {
  name                = "storageaccountname"
  resource_group_name = azurerm_resource_group.example.name

  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "BlobStorage"
}

resource "azurerm_storage_management_policy" "example" {
  storage_account_id = azurerm_storage_account.example.id

  rule {
    name    = "rule1"
    enabled = true
    filters {
      prefix_match = ["container1/prefix1"]
      blob_types   = ["blockBlob"]
      match_blob_index_tag {
        name      = "tag1"
        operation = "=="
        value     = "val1"
      }
    }
    actions {
      base_blob {
        tier_to_cool_after_days_since_modification_greater_than    = 10
        tier_to_archive_after_days_since_modification_greater_than = 50
        delete_after_days_since_modification_greater_than          = 100
      }
      snapshot {
        delete_after_days_since_creation_greater_than = 30
      }
    }
  }
  rule {
    name    = "rule2"
    enabled = false
    filters {
      prefix_match = ["container2/prefix1", "container2/prefix2"]
      blob_types   = ["blockBlob"]
    }
    actions {
      base_blob {
        tier_to_cool_after_days_since_modification_greater_than    = 11
        tier_to_archive_after_days_since_modification_greater_than = 51
        delete_after_days_since_modification_greater_than          = 101
      }
      snapshot {
        change_tier_to_archive_after_days_since_creation = 90
        change_tier_to_cool_after_days_since_creation    = 23
        delete_after_days_since_creation_greater_than    = 31
      }
      version {
        change_tier_to_archive_after_days_since_creation = 9
        change_tier_to_cool_after_days_since_creation    = 90
        delete_after_days_since_creation                 = 3
      }
    }
  }
}
```
<cite> -- Terraform Docs.</cite>

**Performance, scalability**

[Performance and scalability checklist for Azure Blog Storage.](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-performance-checklist)

**Cost planning, optimization**

[Pricing for Azure Blog Storage.](https://learn.microsoft.com/en-us/azure/storage/common/storage-plan-manage-costs?toc=%2Fazure%2Fstorage%2Fblobs%2Ftoc.json&bc=%2Fazure%2Fstorage%2Fblobs%2Fbreadcrumb%2Ftoc.json)

## Analytics

Azure offers a plethora of [products](https://azure.microsoft.com/en-us/products/category/analytics) for Analytics. Choose a service which works for your workloads and use cases. I used Databricks.

# Conclusion

This article was an attempt to provide a reference to various Microsoft Azure services to design and build a scalable, performant and cost-efficient data lake.

These services keep getting updated with newer features from time to time, so the latest Azure documentation will give more information related to them.

Additionally, we touched upon a few topics for which there was excellent Azure documentation, so I just added links to them instead of repeating them here again.

Each data lake effort has a variety of parameters such as available time, people in a team/organization, skills of the team, short term and long term goals for the project, users of the data lake, maintenance effort, operations and so on. It is important to keep these in mind while deciding on design, architecture and implementation.

