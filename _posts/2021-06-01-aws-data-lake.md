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
- [AWS Management Cons-- AWS documentation//docs.aws.amazon.com/whitepapers/latest/aws-overview/compute-services.html).
- [AWS Storage](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/storage-services.html).
- [AWS Analytics](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/analytics.html).
- [AWS Containers](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/containers.html).
- [AWS Application Integration](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/application-integration.html).
- [AWS IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html).
- [What is a Data Lake?](https://aws.amazon.com/what-is/data-lake/)

### Advanced reading
- [AWS Networking Services](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/networking-services.html).
- [AWS Management and Governance](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/management-governance.html).
- [AWS Developer Tools](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/developer-tools.html).
- [Cost management in AWS](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/aws-cost-management.html).
- [AWS Databases](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/database.html).

### Infrastructure as Code
All of the AWS resources discussed can be created manually via the AWS Management Console. 

In a production deployment, that is seldom the case. We typically use an [Infrastructure as Code](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/infrastructure-as-code) deployment to manage resources. There are a few IaC options, Terraform and AWS CDK being the most popular. 

I have worked on both and there are pros and cons with both. 

AWS CDK allows many commonly used languages to define resources - such as Python, Java, TypeScript, Go, JavaScript etc. AWS CDK uses [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-whatis-concepts.html) behind the scenes to deploy resources. It also comes with the same limitations as [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html).

Terraform uses its own [configuration language](https://developer.hashicorp.com/terraform/language) across different clouds, which is convenient if you have a multi-cloud infrastructure. It might take some time to learn Terraform's configuration language, but isn't that difficult as you begin creating and deploying different resources to AWS (or to any other cloud for that matter). Terraform uses declarative syntax as opposed to other common programming langauges.

To illustrate resource creation in this article, I will use Terraform examples for resource creation. 

## What is a Data Lake?
[Reading for this section: What is a Data Lake?](#pre-requisite-reading)
> A data lake is a centralized repository that allows you to store all your structured and unstructured data at any scale. You can store your data as-is, without having to first structure the data, and run different types of analytics—from dashboards and visualizations to big data processing, real-time analytics, and machine learning to guide better decisions.
>
> <cite>-- AWS Documentation.</cite>

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

Sometimes, the S3 bucket containing the data of interest may not reside in the same AWS account from which we are reading it. To begin reading data from such external AWS accounts, the required permissions need to be in place. [Reference article.](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-walkthroughs-managing-access-example4.html)

1. Role in destination account.
2. Role in source/data source account.
3. Trust policy in source/data source account.
4. Access policy related to the source/data source account.

Key roles and policies:
- Access policy for S3 bucket objects - defined in the source AWS account.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::DOC-EXAMPLE-BUCKET1/*"
    }
  ]
}
```
<cite>-- AWS Docs.</cite>

- Trust policy for the source AWS account, allowing the `sts:AssumeRole` action. 

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::source_account-ID:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```
<cite>-- AWS Docs.</cite>

- IAM policy for the destination AWS account, that is, the AWS account which is going to read data from the source AWS account.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["sts:AssumeRole"],
      "Resource": "arn:aws:iam::source_account-ID:role/examplerole"
    }
  ]
}
```
<cite>-- AWS Docs.</cite>

- Steps 2 and 3 need to be followed by 2 new IAM roles in the source and destination AWS accounts respectively and the policies need to be attached to those newly created roles.

The corresponding Terraform code blocks to implement the above IAM role and policies.

```terraform
resource "aws_iam_role" "examplerole" {
  name = "test_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "s3.amazonaws.com"
        }
      },
    ]
  })

  tags = {
    tag-key = "tag-value"
  }
}
```
<cite>-- Terraform Docs.</cite>

- Create a new IAM policy to allow access to S3 buckets.

```terraform
  resource "aws_iam_policy" "s3_access_policy" {
  name        = "s3_access_policy"
  path        = "/"
  description = "My test policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:s3:::DOC-EXAMPLE-BUCKET1/*"
      },
    ]
  })
}
```
<cite>-- Terraform Docs.</cite>

- Attach the new IAM policy to the corresponding IAM role.

```terraform
resource "aws_iam_role_policy_attachment" "test-attach" {
  role       = aws_iam_role.examplerole.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}
```
<cite>-- Terraform Docs.</cite>


### Storage lifecycle and other related items
You might want to consider maintenance of the objects in the S3 bucket, since the data might grow over time. This results in larger partition counts to maintain in addition to growing costs. So, it is a good practice to define a lifecycle configuration for the S3 objects. 

> An S3 Lifecycle configuration is an XML file that consists of a set of rules with predefined actions that you want Amazon S3 to perform on objects during their lifetime.
>
> <cite>-- AWS Documentation.</cite>

The objects can be [set](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_lifecycle_configuration#creating-a-lifecycle-configuration-for-a-bucket-with-versioning) to either transition to another storage class or to expire after a certain time period.

```terraform
resource "aws_s3_bucket_lifecycle_configuration" "versioning-bucket-config" {
  # Must have bucket versioning enabled first
  depends_on = [aws_s3_bucket_versioning.versioning]

  bucket = aws_s3_bucket.versioning_bucket.id

  rule {
    id = "config"

    filter {
      prefix = "config/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }

    noncurrent_version_transition {
      noncurrent_days = 60
      storage_class   = "GLACIER"
    }

    status = "Enabled"
  }
}
```
<cite>-- Terraform Docs.</cite>

### Security
Securing the objects in AWS S3 buckets is important. Some configurations to consider:
1. Encryption.
2. Public access block.
3. Logging.
4. Notifications. 
5. Metrics.

**Encryption**
The option encrypts the S3 bucket and all objects inside the bucket. It is a good practice to enable this when creating the bucket to ensure all current and future objects are encrypted.

[Related AWS Doc.](https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-encryption-faq.html)

```terraform
resource "aws_kms_key" "mykey" {
  description             = "This key is used to encrypt bucket objects"
  deletion_window_in_days = 10
}

resource "aws_s3_bucket" "mybucket" {
  bucket = "mybucket"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.mybucket.id

  rule {https://repost.aws/knowledge-center/s3-large-transfer-between-buckets
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.mykey.arn
      sse_algorithm     = "aws:kms"
    }
  }
}
```
<cite>-- Terraform Docs.</cite>

**Public access block**
AWS recommends blocking public access of S3 objects, especially when dealing with sensitive data. It also recommends setting all 4 options to true (see below). 

[Related AWS Doc.](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.htmls)

```terraform
resource "aws_s3_bucket" "example" {
  bucket = "example"
}

resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.example.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```
<cite>-- Terraform Docs.</cite>

**Logging**
Allows logging of all access requests to the S3 bucket. The logs are stored in a separate S3 bucket, with appropriate permissions.

[Related AWS Doc.](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html)

```terraform
resource "aws_s3_bucket" "example" {
  bucket = "my-tf-example-bucket"
}

resource "aws_s3_bucket_acl" "example" {
  bucket = aws_s3_bucket.example.id
  acl    = "private"
}

resource "aws_s3_bucket" "log_bucket" {
  bucket = "my-tf-log-bucket"
}

resource "aws_s3_bucket_acl" "log_bucket_acl" {
  bucket = aws_s3_bucket.log_bucket.id
  acl    = "log-delivery-write"
}

resource "aws_s3_bucket_logging" "example" {
  bucket = aws_s3_bucket.example.id

  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "log/"
}
```
<cite>-- Terraform Docs.</cite>

**Notifications**
AWS SNS can be enabled for an S3 bucket to be notified when specified events occur. 

[Related AWS Doc.](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventNotifications.html)

```terraform
  data "aws_iam_policy_document" "topic" {
    statement {
      effect = "Allow"

      principals {
        type        = "Service"
        identifiers = ["s3.amazonaws.com"]
      }

      actions   = ["SNS:Publish"]
      resources = ["arn:aws:sns:*:*:s3-event-notification-topic"]

      condition {
        test     = "ArnLike"
        variable = "aws:SourceArn"
        values   = [aws_s3_bucket.bucket.arn]
      }
    }
  }
  resource "aws_sns_topic" "topic" {
    name   = "s3-event-notification-topic"
    policy = data.aws_iam_policy_document.topic.json
  }

  resource "aws_s3_bucket" "bucket" {
    bucket = "your-bucket-name"
  }

  resource "aws_s3_bucket_notification" "bucket_notification" {
    bucket = aws_s3_bucket.bucket.id

    topic {
      topic_arn     = aws_sns_topic.topic.arn
      events        = ["s3:ObjectCreated:*"]
      filter_suffix = ".log"
    }
  }
```
<cite>-- Terraform Docs.</cite>

**Metrics**
Monitors and records overall metrics related to the S3 bucket. Can be customized to monitor the entire bucket or can be set to specific filters.

[Related AWS Doc.](https://docs.aws.amazon.com/AmazonS3/latest/userguide/metrics-configurations.html)

```terraform
  # For the entire S3 bucket
  resource "aws_s3_bucket" "example" {
    bucket = "example"
  }

  resource "aws_s3_bucket_metric" "example-entire-bucket" {
    bucket = aws_s3_bucket.example.id
    name   = "EntireBucket"
  }

  # With filters
  resource "aws_s3_bucket" "example" {
    bucket = "example"
  }

  resource "aws_s3_bucket_metric" "example-filtered" {
    bucket = aws_s3_bucket.example.id
    name   = "ImportantBlueDocuments"

    filter {
      prefix = "documents/"

      tags = {
        priority = "high"
        class    = "blue"
      }
    }
  }
```
<cite>-- Terraform Docs.</cite>

### Cost
It is important to keep an eye on costs, especially when handling Terabytes or Petabytes of data in your Data Lake. The first step to manage costs is to monitor it. One of the many ways to monitor costs in AWS is the [AWS Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html) service. Please note that there is a nominal cost to make API calls to the CE service.

Terraform allows defining some options to define Cost Explorer resources:

```terraform
resource "aws_ce_anomaly_monitor" "service_monitor" {
  name              = "AWSServiceMonitor"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"
}
```
<cite>-- Terraform Docs.</cite>

Another alternative to view your spending is the comprehensive AWS [Cost and Usage report](https://docs.aws.amazon.com/cur/latest/userguide/what-is-cur.html). This service allows sending data in CSV format to an S3 bucket from which you can visualize the cost data via one of the available [AWS reporting services](https://docs.aws.amazon.com/cur/latest/userguide/what-is-cur.html#download-cur).

Defining a Cost and Usage report resource via Terraform:

```terraform
resource "aws_cur_report_definition" "example_cur_report_definition" {
  report_name                = "example-cur-report-definition"
  time_unit                  = "HOURLY"
  format                     = "textORcsv"
  compression                = "GZIP"
  additional_schema_elements = ["RESOURCES", "SPLIT_COST_ALLOCATION_DATA"]
  s3_bucket                  = "example-bucket-name"
  s3_region                  = "us-east-1"
  additional_artifacts       = ["REDSHIFT", "QUICKSIGHT"]https://repost.aws/knowledge-center/s3-large-transfer-between-buckets
}
```
<cite>-- Terraform Docs.</cite>

Another way to reduce data transfer and networking costs is to keep the data closer to its source when building the data lake. 

Some options:
- Storing the data in an AWS S3 bucket belonging to the same region as the data sources.
- Analyzing data in the same region and then sending only relevant data (such as as summaries or reports etc.) across different AWS regions. 

Each service in AWS has its own pricing, so it important to note them and use them accordingly. 

### Data ingestion between source and destination AWS S3 buckets
There are many ways to transfer large volumes of data between two S3 buckets. AWS describes them very well [here](https://repost.aws/knowledge-center/s3-large-transfer-between-buckets). 

Additionally, one other option is to setup downstream trigger jobs to run when a new event occurs in the AWS S3 bucket. We previously discussed setting up [notifications](#security) for events in AWS S3 buckets. The same setup can be used here. Once the SNS is setup, the destination AWS account can listen to these notifications via the AWS Simple Queue Service (SQS). The implementation is discussed [here](https://docs.aws.amazon.com/sns/latest/dg/sns-send-message-to-sqs-cross-account.html). Once the message is received from the Queue, you can write your own [application](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/examples-sqs-messages.html#sqs-messages-receive) to ingest the data and write it to a destination of your choice, which could be another AWS S3 bucket or a Delta table etc.

## AWS Kinesis
One of the most popular ways of sending and receiving large volumes of data is AWS Kinesis, via streaming. This is one of the most comprehensive [whitepapers](https://d0.awsstatic.com/whitepapers/whitepaper-streaming-data-solutions-on-aws-with-amazon-kinesis.pdf) explaining different Kinesis use cases as well as tooling/services to consume/sink data from Kinesis.

Since the whitepaper explains everything in detail, I will not elaborate on different options available with Kinesis.

## External data sources
### From an on-premise source 
### From another cloud provider
### Others
Flat files
Spreadsheets
SaaS systems/APIs 

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
### Redshift
**Usage**
**Performance and scaling**
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