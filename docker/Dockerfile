FROM bitnami/spark:latest

COPY ../src /opt/spark-app
WORKDIR /opt/spark-app

CMD ["spark-submit", "streaming_job.py"]
