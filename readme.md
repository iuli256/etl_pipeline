# Project Datawarehouse

## Introduction

In this project I build an ETL pipeline that extracts their data from AWS S3 (data storage), stages tables on AWS Redshift (data warehouse with columnar storage), and execute SQL statements that create the analytics tables from these staging tables.

### Datasets
Datasets used in this project are provided in two public S3 buckets. One bucket contains info about songs and artists, the second bucket has info concerning actions done by users (which song are listening, etc.. ). The objects contained in both buckets are JSON files.

The Redshift service is where data will be ingested and transformed, in fact though COPY command we will access to the JSON files inside the buckets and copy their content on our staging tables.

### Database Schema
We have two staging tables which copy the JSON file inside the S3 buckets.

### Staging Table
<b>staging_songs</b> - info about songs and artists  
<b>staging_events</b> - actions done by users (which song are listening, etc.. ) 
I createa a star schema optimized for queries on song play analysis. This includes the following tables.

### Fact Table
<b>songplays</b> - records in event data associated with song plays i.e. records with page NextSong

### Dimension Tables
<b>users</b> - users in the app  
<b>songs</b> - songs in music database  
<b>artists</b> - artists in music database  
<b>time</b> - timestamps of records in songplays broken down into specific units  

The database schema is shown as follows
![Alt text](images/ER-Diagram.png?raw=true "Title")
### Data Warehouse Configurations and Setup
Create a new IAM user in your AWS account 
Give it AdministratorAccess and Attach policies  
Use access key and secret key to create clients for EC2, S3, IAM, and Redshift.  
Create an IAM Role that makes Redshift able to access S3 bucket (ReadOnly)  
Create a RedShift Cluster and get the DWH_ENDPOIN(Host address) and DWH_ROLE_ARN and fill the config file.  
### ETL Pipeline
Created tables to store the data from S3 buckets.  
Loading the data from S3 buckets to staging tables in the Redshift Cluster.  
Inserted data into fact and dimension tables from the staging tables.  
### Project Structure
create_tables.py - This script will drop old tables (if exist) ad re-create new tables.  
etl.py - This script executes the queries that extract JSON data from the S3 bucket and ingest them to Redshift.  
sql_queries.py - This file contains variables with SQL statement in String formats, partitioned by CREATE, DROP, COPY and INSERT statement.  
dhw.cfg - Configuration file used that contains info about Redshift, IAM and S3

## How to run

1. To run this project you will need to fill the following information, and save it as *dwh.cfg* in the project root folder.  
Make sure that the user you have created on AWS has a IAM_ROLE permision `AdministratorAccess`   
After the cluster is created on console will be shown  
DWH_ENDPOINT ::  xxxxxx  
DWH_ROLE_ARN ::  xxxxxx  
The value of `DWH_ENDPOINT` have to be copied on dwh.cfg `[CLUSTER] HOST=` and the value of `DWH_ROLE_ARN` have to be copied on dwh.cfg `[IAM_ROLE] ARN=`
```
[CLUSTER]
HOST=''
DB_NAME=''
DB_USER=''
DB_PASSWORD=''
DB_PORT=5439

[IAM_ROLE]
ARN=

[S3]
LOG_DATA='s3://udacity-dend/log_data'
LOG_JSONPATH='s3://udacity-dend/log_json_path.json'
SONG_DATA='s3://udacity-dend/song_data'

[AWS]
KEY=
SECRET=

[DWH]
DWH_CLUSTER_TYPE       = multi-node
DWH_NUM_NODES          = 4
DWH_NODE_TYPE          = dc2.large
DWH_CLUSTER_IDENTIFIER = 
DWH_DB                 = 
DWH_DB_USER            = 
DWH_DB_PASSWORD        = 
DWH_PORT               = 5439
DWH_IAM_ROLE_NAME      = 
```

2. First we have to run the *redshif_cluster* script to set up the needed infrastructure for this project. This file have to be runned several times because the cluster it will be created in about 2 minutes and because of that we have to runn it few times in order to be able to apply all the rules. After it finish you have to copy the `DWH_ENDPOINT` value to `[CLUSTER] HOST` and `DWH_ROLE_ARN` to `[IAM_ROLE] ARN` 

    `$ python redshift_cluster.py create`

4. Run the *create_tables* script to set up the database staging and analytical tables

    `$ python create_tables.py`

5. Finally, run the *etl* script to extract data from the files in S3, stage it in redshift, and finally store it in the dimensional tables.

    `$ python etl.py`

6. To delete the cluster you have to run *redshif_cluster* script 

    `$ python redshift_cluster.py delete`
 
## Queries and Results

Number of rows in each table:
```
| Table            | rows  |  
|---               | --:   |  
| staging_events   |  8056 |  
| staging_songs    | 14896 |  
| artists          | 10025 |  
| songplays        |   333 |  
| songs            | 14896 |  
| time             |   333 |  
| users            |   104 |  
```

### Steps followed on this project

#### Create Table Schemas
- Design schemas for your fact and dimension tables
- Write a SQL CREATE statement for each of these tables in sql_queries.py
- Complete the logic in create_tables.py to connect to the database and create these tables
- Write SQL DROP statements to drop tables in the beginning of - create_tables.py if the tables already exist. This way, you can run create_tables.py whenever you want to reset your database and test your ETL pipeline.
- Launch a redshift cluster and create an IAM role that has read access to S3.
- Add redshift database and IAM role info to dwh.cfg.
- Test by running create_tables.py and checking the table schemas in your redshift database. You can use Query Editor in the AWS Redshift console for this.

#### Build ETL Pipeline
- Implement the logic in etl.py to load data from S3 to staging tables on Redshift.
- Implement the logic in etl.py to load data from staging tables to analytics tables on Redshift.
- Test by running etl.py after running create_tables.py and running the analytic queries on your Redshift database to compare your results with the expected results.
- Delete your redshift cluster when finished.

#### Document Process
Do the following steps in README.md file.
