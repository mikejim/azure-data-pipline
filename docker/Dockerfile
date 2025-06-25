FROM bitnami/spark:latest

# Copy your Spark app
COPY ../src /opt/spark-app
WORKDIR /opt/spark-app

# Create JAR folder
RUN mkdir -p /opt/bitnami/spark/jars

# --- Add Spark Kafka connector ---
RUN curl -L -o /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.4.1.jar https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.4.1/spark-sql-kafka-0-10_2.12-3.4.1.jar && \
    curl -L -o /opt/bitnami/spark/jars/kafka-clients-3.5.1.jar https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar

# --- Add Azure ABFS support ---
RUN curl -L -o /opt/bitnami/spark/jars/hadoop-azure-3.3.2.jar https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-azure/3.3.2/hadoop-azure-3.3.2.jar && \
    curl -L -o /opt/bitnami/spark/jars/azure-storage-8.6.6.jar https://repo1.maven.org/maven2/com/microsoft/azure/azure-storage/8.6.6/azure-storage-8.6.6.jar

# Run your Spark job
CMD ["spark-submit", "streaming_job.py"]
