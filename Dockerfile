FROM apache/airflow:2.10.2

USER airflow

RUN pip install psycopg2-binary

