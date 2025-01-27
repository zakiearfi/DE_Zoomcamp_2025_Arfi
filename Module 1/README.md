# New York Green Line Trip Data Ingestion & Analysis

## Overview
In this project, I implemented a data ingestion pipeline by preparing a PostgreSQL database in a Dockerized environment to serve as the initial data storage. Additionally, I set up a bucket and dataset in BigQuery for scalable and efficient data processing and analytics. The infrastructure provisioning and resource configuration were automated using Terraform, ensuring consistency, repeatability, and seamless deployment across environments. This approach streamlined the data flow from the source to the target storage, enabling efficient data management and integration.

## Docker Setup

### Create a network for Postgre
```bash
docker network create pg-network
```

### PostgreSQL Container
Run the following Docker command to start a PostgreSQL container:
```bash
docker run -it \
  -e POSTGRES_USER="postgres" \
  -e POSTGRES_PASSWORD="postgres" \
  -e POSTGRES_DB="ny_taxi" \
  -p 5432:5432 \
  -v c:/Users/zakie/git/2_docker_sql/ny_taxi_postgres_data:/var/lib/postgresql/data  \
  --network=pg-network \
  --name pg-database \
  postgres:17-alpine
```

### PGAdmin Container
Launch a pgAdmin container with the following command:
```bash
docker run -it \
  -p 8080:80 \
  -e PGADMIN_DEFAULT_EMAIL='admin@admin.com' \
  -e PGADMIN_DEFAULT_PASSWORD='root' \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4:latest
```

## Building Data Pipeline

### Ingest via Python
```bash
URL1="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz"
URL2="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

python ingest_data.py \
  --user=postgres \
  --password=postgres\
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --table1=green_trip_data \
  --table2=taxi_zone_lookup \
  --url1=${URL1} \
  --url2=${URL2}
```

### Docker Image
Build a Docker image for the data ingestion pipeline:

```bash
docker build -t taxi_data_ingestion:v001 .
```
### Running Data Pipeline Container
Run the data ingestion pipeline container:
```bash
docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
    --user=postgres \
    --password=postgres\
    --host=pg-database \
    --port=5432 \
    --db=ny_taxi \
    --table1=green_trip_data \
    --table2=taxi_zone_lookup \
    --url1=${URL1} \
    --url2=${URL2}
```
## Docker Compose

Docker Compose is used to orchestrate multiple containers. It provides a way to define and run multi-container Docker applications. In this project, it is used to define and run the entire stack in a more organized manner.

To deploy the entire stack using Docker Compose:

```bash
docker-compose up
```

In detached mode:

```bash
docker-compose up -d
```

To stop the containers:

```bash
docker-compose down
```

## Terraform Setup

1. Install Terraform and add it to your system path.
2. Initialize Terraform:

    ```bash
    terraform init
    ```

3. View the planned changes:

    ```bash
    terraform plan
    ```

4. Deploy the architecture:

    ```bash
    terraform apply
    ```


## Overview Homework
here is the explanation of the answers. all the documentations are store as a screenshot on folder Data/Answers (note: answer number 3-6 can check on [homework_question.sql](homework_question.sql)):

### Question 1. Understanding docker first run
Run docker with the python:3.12.8 image in an interactive mode, use the entrypoint bash.
What's the version of pip in the image?

```bash
$ docker run -it python:3.12.8 bash
root@795c80305dcd:/# pip --version
pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```

### Question 2. Understanding Docker networking and docker-compose
Given the following docker-compose.yaml, what is the hostname and port that pgadmin should use to connect to the postgres database?

Based on the docker-compose.yaml, the valid answer is:

- db:5432
- postgres:5432

Reason:

- "db" is the name of the service in docker-compose
- "postgres" is the container_name defined for the database service
- The container's internal port is 5432, not 5433 (5433 is the external mapping port)

### Question 3
During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, respectively, happened:

Up to 1 mile
In between 1 (exclusive) and 3 miles (inclusive),
In between 3 (exclusive) and 7 miles (inclusive),
In between 7 (exclusive) and 10 miles (inclusive),
Over 10 miles

```bash
'''question number 3: Trip Segmentation Count'''
WITH trip_counts AS (
    SELECT 
        COUNT(*) AS total_trips,
        SUM(CASE WHEN trip_distance <= 1 THEN 1 ELSE 0 END) AS trips_up_to_1_mile,
        SUM(CASE WHEN trip_distance > 1 AND trip_distance <= 3 THEN 1 ELSE 0 END) AS trips_1_to_3_miles,
        SUM(CASE WHEN trip_distance > 3 AND trip_distance <= 7 THEN 1 ELSE 0 END) AS trips_3_to_7_miles,
        SUM(CASE WHEN trip_distance > 7 AND trip_distance <= 10 THEN 1 ELSE 0 END) AS trips_7_to_10_miles,
        SUM(CASE WHEN trip_distance > 10 THEN 1 ELSE 0 END) AS trips_over_10_miles
    FROM green_trip_data
    WHERE DATE(lpep_pickup_datetime) >= '2019-10-01' 
      AND DATE(lpep_dropoff_datetime) < '2019-11-01'
```

### Question Number 4
Which was the pick up day with the longest trip distance? Use the pick up time for your calculations.

Tip: For every day, we only care about one single trip with the longest distance.

```bash
WITH daily_max_distance AS (
    SELECT 
        DATE(lpep_pickup_datetime) as pickup_date,
        MAX(trip_distance) as max_distance
    FROM green_trip_data
    WHERE DATE(lpep_pickup_datetime) IN ('2019-10-11', '2019-10-24', '2019-10-26', '2019-10-31')
    GROUP BY DATE(lpep_pickup_datetime)
)
SELECT 
    pickup_date,
    max_distance
FROM daily_max_distance
ORDER BY max_distance DESC;
``` 

### Question Number 5
Which were the top pickup locations with over 13,000 in total_amount (across all trips) for 2019-10-18?

Consider only lpep_pickup_datetime when filtering by date.

```bash
SELECT 
    g."PULocationID",
    z."Zone" as pickup_zone,
    z."Borough" as borough,
    SUM(g.total_amount) as total_sum
FROM green_trip_data g
JOIN taxi_zone_lookup z 
    ON g."PULocationID" = z."LocationID"
WHERE DATE(g.lpep_pickup_datetime) = '2019-10-18'
GROUP BY 
    g."PULocationID",
    z."Zone",
    z."Borough"
HAVING SUM(g.total_amount) > 13000
ORDER BY total_sum DESC;
```

### Question Number 6
For the passengers picked up in October 2019 in the zone named "East Harlem North" which was the drop off zone that had the largest tip?

Note: it's tip , not trip

We need the name of the zone, not the ID.

```bash
SELECT 
    dropoff_zone."Zone" as dropoff_zone_name,
    MAX(g.tip_amount) as max_tip
FROM green_trip_data g
JOIN taxi_zone_lookup pickup_zone 
    ON g."PULocationID" = pickup_zone."LocationID"
JOIN taxi_zone_lookup dropoff_zone 
    ON g."DOLocationID" = dropoff_zone."LocationID"
WHERE 
    DATE_TRUNC('month', g.lpep_pickup_datetime) = '2019-10-01'
    AND pickup_zone."Zone" = 'East Harlem North'
GROUP BY dropoff_zone."Zone"
ORDER BY max_tip DESC;
```

### Question Number 7
Which of the following sequences, respectively, describes the workflow for:

Downloading the provider plugins and setting up backend,
Generating proposed changes and auto-executing the plan
Remove all resources managed by terraform`

**Answer:**
```bash
terraform init, terraform apply -auto-approve, terraform destroy
```