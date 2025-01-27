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
)
SELECT * FROM trip_counts;

'''question number 4: Longest trip for each day'''
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

'''question number 5: Three biggest pickup zones'''
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

'''question number 6: Largest tip'''
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