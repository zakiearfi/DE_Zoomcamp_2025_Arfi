#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from time import time
from sqlalchemy import create_engine
import argparse
import os
from urllib.parse import urlparse
import requests
import gzip
import shutil

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table1 = params.table1
    table2 = params.table2
    url1 = params.url1
    url2 = params.url2

     # Get green taxi data from the URL
    url_path1 = urlparse(url1).path
    csv_name1 = os.path.basename(url_path1)
    
    # Get taxi zone data from the URL
    url_path2 = urlparse(url2).path
    csv_name2 = os.path.basename(url_path2)

    # If the file is gzipped, remove the '.gz' extension
    if csv_name1.endswith('.csv.gz'):
        csv_name1 = csv_name1.replace('.gz', '')

    # Download the file using requests
    response = requests.get(url1)

    # Download taxi zone data using requests
    response2 = requests.get(url2)

    # Save the file
    with open(csv_name2, 'wb') as file2:
        file2.write(response2.content)

    # Save compressed content to a file
    compressed_file_path = csv_name1 + '.gz'
    with open(compressed_file_path, 'wb') as compressed_file:
        compressed_file.write(response.content)

    # Extract the compressed file
    extracted_file_path = csv_name1
    with gzip.open(compressed_file_path, 'rb') as f_in:
        with open(extracted_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)    
    
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    engine.connect()

    df_zone = pd.read_csv(csv_name2)
    df_zone.to_sql(name=table2, con=engine, if_exists='replace')
    df_iter_green = pd.read_csv(extracted_file_path, iterator=True, chunksize=20000)

    df_green = next(df_iter_green)

    df_green.lpep_pickup_datetime = pd.to_datetime(df_green.lpep_pickup_datetime, errors='coerce')
    df_green.lpep_dropoff_datetime = pd.to_datetime(df_green.lpep_dropoff_datetime, errors='coerce')

    df_green.head(n=0).to_sql(name=table1, con=engine, if_exists='replace')

    # Unggah chunk pertama
    t_start = time()
    df_green.to_sql(name=table1, con=engine, if_exists='append')
    t_end = time()
    print(f"Inserted first chunk, took {t_end - t_start:.3f} seconds")

    while True:
        try:
            t_start = time()

            df_green = next(df_iter_green)

            df_green.lpep_pickup_datetime = pd.to_datetime(df_green.lpep_pickup_datetime, errors='coerce')
            df_green.lpep_dropoff_datetime = pd.to_datetime(df_green.lpep_dropoff_datetime, errors='coerce')

            df_green.to_sql(name=table1, con=engine, if_exists='append')

            t_end = time()
            print('inserted another chunk, took %.3f second' % (t_end - t_start))
        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break # break the loop when the end of the file is reached

        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    # add argument for user, password, host, port, database name, table name, url of the csv
    parser.add_argument("--user", help="Postgres user")
    parser.add_argument("--password", help="Postgres password")
    parser.add_argument("--host", help="Postgres host")
    parser.add_argument("--port", help="Postgres port")
    parser.add_argument("--db", help="Postgres database name")
    parser.add_argument("--table1", help="Postgres table name")
    parser.add_argument("--table2", help="Postgres table name")
    parser.add_argument("--url1", help="URL of the CSV file")
    parser.add_argument("--url2", help="URL of the 2nd CSV file")

    args = parser.parse_args()

    main(args)