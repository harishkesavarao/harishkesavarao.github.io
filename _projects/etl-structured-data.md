---
layout: page
title: Parsing data from structured data sources.
description: Parsing and transforming structured data.
importance: 1
category: side-projects
---

# Introduction
I worked on this project a few years ago.

We had many Microsoft Excel sheets containing information about product versions. Each of these documents had many versions and each product line also had a document of its own.

# Use cases
Users of this data wanted a centralised location from which they could search, view and visualize the data. If a new version of the document is released, or if an existing document is updated, the destination dataset should reflect those as well.

## Considerations
1. The data should be available for analysis - using interactive querying and/or visualization methods.
2. The data should refresh automatically via batch jobs when there is new data. Additionally, this introduces the additional use case of detecting new data. 
3. The data should be secure and should be available to only a list of allowed individuals.

# Extraction
Instead of focusing on the extraction first, I started to think of different ways in which one could store the data and then build a pipeline to read from the data sources.

Based on the considerations above, the storage destination should be persisted. Some choices were:
1. Relational databases. 
2. Spreadsheets.
3. Other semi-structured formats such as JSON. 

I will discuss more on the storage destination in its own section below, and will now start discussing the design of landing the data to the destination.

## Design choices:
1. ETL tools.
2. Connectivity from Microsoft Excel to Microsoft SQL Server (or any relational database).
3. Custom scripting. 

### Off-the-shelf ETL tools.
I considered a host of options to reliably extract data from an XLSX document. Initially, I explored readily available products, such as contemporary ETL tools (Informatica et al.). I performed small, quick Proof Of Concept exercises to test the feasibility of the different tools. The tools were able to connect with the XSLX files and extract data, but I ran into the following challenges:
- The connectivity mainly depended on ODBC drivers, which could not be customized to suit the use case -- such as parsing through different sheets in the same document or extracting cells based on specific conditions. 
- The tools were able to successfully connect and extract entire sheets into relational database tables. However, the data has to be completely imported in its raw state as tables and that caused complexities. The raw state could not be completely transformed to the desired structure, once it was imported into the ETL tool. 
- The customizations were too cumbersome, given the limited options within the tools. Also, some tools allow scripting to be embedded into the ETL pipeline, which does help, but that also led to the idea of scripting the entire solution end-to-end, which is what I ended up doing, since it was very customizable and, at the same time, easier to develop from scratch.

### Connecting MS Excel to MS SQL Server directly
A second option was to try to connect to Microsoft SQL Server from Microsoft Excel. Microsoft has a plethora of [options](https://learn.microsoft.com/en-us/sql/relational-databases/import-export/import-data-from-excel-to-sql?view=sql-server-ver16) to do so. And all of these options work quite well. The problem for this use case is customization and the final structure of the dataset. 

This option could have been pursued by an ELT pipeline/connection, where you land all the data as-is from Microsoft Excel to Microsoft SQL Server and then perform all the transformations inside MS SQL Server using ANSI SQL. The documents are created and uploaded manually to Microsoft Sharepoint, so the feature of detecting updates to existing documents or detecting the arrival of new documents would be available. 

This will work quite well, but it did come with some [restrictions](https://learn.microsoft.com/en-us/sql/integration-services/load-data-to-from-excel-with-ssis?view=sql-server-ver16#issues-importing).It also requires using Microsoft SSIS along with MS SQL Server, adding to the number of hops for the data as well as complexity.

### Custom scripting
Finally, having decided to pursue the scription route, I decided to use Python. Based on my past experience with Python for similar use cases (professionally as well as in other side projects),  it is best suited for data analysis due to its large library support for data exploration, modification and analysis. Python also allows using a variety of built-in libraries, including Pandas, which makes data transformation even simpler and customizable. 

## Transformation
Going back to the considerations section, we have both querying and reporting use cases. As I explained the extraction section above as well as the storage section below, the destination is a relational database.  

The most suited structure to allow efficient reporting is a [star schema](https://www.kimballgroup.com/1997/08/a-dimensional-modeling-manifesto/). 

### Implementation steps
1. Extract the data from the MS Excel sheets via Python. This includes the logic to identify and parse all the relevant files, to detect changes to existing files and to detect newly added files.
2. Write the required/selected data from the sheets/documents into a staging schema in MS SQL Server.
3. Write an ETL flow to convert the transactional schema to a dimensional schema, with appropriate dimensions and facts.

### Some nuances and additional facts related to the above steps

Initially, I explored Pandas to extract and transform the data. However, due to the structure of the data, this method proved cumbersome and slow. The entire dataset had to be read into a Pandas Dataframe and selection, filtering and data presentation for the final step was tedious. 

So, I used the 

## Storage and Business Intelligence


# Conclusion
