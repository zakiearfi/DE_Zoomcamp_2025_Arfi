FROM python:3.12.8

RUN pip install pandas sqlalchemy psycopg2
RUN apt-get install wget
RUN pip install argparse
RUN pip install requests

WORKDIR /app
COPY ingest_data.py ingest_data.py

ENTRYPOINT [ "python", "ingest_data.py" ]