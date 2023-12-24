---
layout: post
title: Building a data lake on Amazon Web Services.
date: 2021-06-01 05:18:00
description: Building and deploying a data lake on AWS infrastructure.
related_posts: false
tags: bigdata aws data-engineering scala
featured: false
toc: 
  beginning: true
---

# Introduction
## Pre-requisite reading
In order to fully understand or follow along with the article, I recommend reading some of the documents, articles and other links I have included in this section. If you have already worked on the AWS services I have listed below, you can skip this section.

- [AWS Cloud essentials](https://aws.amazon.com/getting-started/cloud-essentials/).
- [AWS Services by category](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/amazon-web-services-cloud-platform.html?pg=cloudessentials).
- [AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html).
- [AWS Accounts](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts.html).
- [AWS Management Console](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/accessing-aws-services.html).
- [AWS Compute](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/compute-services.html).
- [AWS Storage](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/storage-services.html).
- [AWS Analytics](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/analytics.html).
- [AWS Containers](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/containers.html).
- [AWS Application Integration](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/application-integration.html).
- [AWS IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html).
- [What is a Data Lake](https://aws.amazon.com/what-is/data-lake/).

### Advanced reading
- [AWS Networking Services](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/networking-services.html).
- [AWS Management and Governance](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/management-governance.html).
- [AWS Developer Tools](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/developer-tools.html).
- [Cost management in AWS](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/aws-cost-management.html).
- [AWS Databases](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/database.html).

## What is a Data Lake?
[Reading for this section: What is a Data Lake](#pre-requisite-reading)
> A data lake is a centralized repository that allows you to store all your structured and unstructured data at any scale. You can store your data as-is, without having to first structure the data, and run different types of analytics—from dashboards and visualizations to big data processing, real-time analytics, and machine learning to guide better decisions.

# Use cases
It is cost effective and performant to build a Data Lake when the data volume is over a certain threshold. The threshold is usually in the tens of GBs of data per day and continues to accumulate over time. If the data volume is less than that, it would be quicker and cheaper to build a traditional data warehouse or other solutions.

As we saw above, a Data Lake is a centralized repository which stores all of the structured and unstructured data. This means that this data is available to anyone in an organization (with the relevant permissions). This could be - Data Analysts, Data Scientists, Data Engineers, Business Analysts, Product Managers, Finance or any other function. This offers a single source of truth of the data and each sub-function or department within an organization can choose to use the data as they see fit, with their own tooling for data access, analytics and visualization.


# Architecture
First, we will try to see the different pieces of a typical big data flow. Then, we can explore the different options available in AWS to accommodate those pieces. This will help us arrive at our actual architecture diagram which will more closely represent our actual implementation.

`TODO: Data Flow Diagram`


# Data sources
Typically, data sources come from within AWS itself. In rare exceptions, the data comes from outside the cloud, or from another cloud provider. We will discuss both scenarios.

## AWS S3
[AWS S3 (Simple Storage Service)](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html) is one of the most common use cases of consuming data in AWS. You can read about the basics (buckets, etc.) of S3 from the documentation link.
### Cross-account storage
[Reading for this section: AWS Organizations and AWS Accounts](#pre-requisite-reading)
Sometimes, the S3 bucket containing the data of interest may not reside in the same AWS account from which we are reading it. To begin reading from such external accounts, the required permissions need to be in place.



### Storage lifecycle and other related items
### Security
### Encryption
### Cost
#### Multi-region data

## Redshift
### Analytics
### Performance and scaling

## Kinesis

## Cloudwatch

## External data sources
### From an on-premise source 
### From another cloud provider
### Others
Flat files
Spreadsheets
SaaS systems/APIs 

# Destination

# Design decisions, trade-offs 
## Compute
### EC2
### EMR
### SageMaker

## Storage
### S3

# ETL
## Security and permissions


## Batch vs. Streaming

# Costs and Scaling up/down
## Compute
## Storage
## In-flight data

# Alerting and Monitoring
## Cloudwatch
## Eventbridge

## Performance Tuning

# Analytics
## Cataloging, accuracy and governance

## Tooling
### Quicksight
### Sagemaker
### Tableau

# Reference Architecture Diagram

`TODO: Architecture Diagram`

## DevOps
### Terraform
### AWS CDK
### Code/Application

# Conclusion