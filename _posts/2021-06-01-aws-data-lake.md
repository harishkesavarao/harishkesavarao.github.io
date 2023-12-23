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
## What is a Data Lake?
> A data lake is a centralized repository that allows you to store all your structured and unstructured data at any scale. You can store your data as-is, without having to first structure the data, and run different types of analytics—from dashboards and visualizations to big data processing, real-time analytics, and machine learning to guide better decisions.

The AWS website has a good [article](https://aws.amazon.com/what-is/data-lake/) which explains more about a Data Lake and how it compares to a traditional data warehouse, 

# Use cases
It is cost effective and performant to build a Data Lake when the data volume is over a certain threshold. The threshold is usually in the tens of GBs of data per day and continues to accumulate over time. If the data volume is less than that, it would be quicker and cheaper to build a traditional data warehouse or other solutions.

As we saw above, a Data Lake is a centralized repository which stores all of the structured and unstructured data. This means that this data is available to anyone in an organization (with the relevant permissions). This could be - Data Analysts, Data Scientists, Data Engineers, Business Analysts, Product Managers, Finance or any other function. This offers a single source of truth of the data and each sub-function or department within an organization can choose to use the data as they see fit, with their own tooling for data access, analytics and visualization.


# Architecture
First, we will try to see the different pieces of a typical big data flow. Then, we can explore the different options available in AWS to accomodate those pieces. This will help us arrive at our actual architecture diagram which will more closely represent our actual implementation.

`TODO: Data Flow Diagram`


# Data sources
Typically, data sources come from within AWS itself. In rare exceptions, the data comes from outside the cloud, or from another cloud provider. We will discuss both scenarios.

## AWS S3
[AWS S3 (Simple Storage Service)](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html) is one of the most common use cases of consuming data in AWS. You can read about the basics (buckets, etc.) of S3 from the documentation link.
### Storage
When talking about ingesting/reading data from S3, or interacting with other AWS services for that matter, there are some items to note. The S3 bucket containing the data of interest may or may not reside in the same AWS account from which we are reading it. To understand more about AWS accounts, AWS organizations need to be discussed as well. You can read more about it [here](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html). Read this [documentation](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts.html) to know more about how AWS organizations and AWS accounts are related.
### Retention
### Versioning
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