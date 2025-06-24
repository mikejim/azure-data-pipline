from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType

import os

# Load environment variables
EVENT_HUB_CONNECTION_STRING = os.getenv("EVENT_HUB_CONNECTION_STRING")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "sparkdatalakemj202506")
FILESYSTEM_NAME = os.getenv("FILESYSTEM_NAME", "spark-output")

# Define schema for incoming JSON
schema = StructType() \
    .add("user_id", StringType()) \
    .add("movie_id", StringType()) \
    .add("watch_time", IntegerType()) \
    .add("timestamp", StringType())

# Output path on ADLS Gen2
output_path = f"abfss://{FILESYSTEM_NAME}@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/events/"

# Checkpoint path
checkpoint_path = f"abfss://{FILESYSTEM_NAME}@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/checkpoints/streaming/"

# Create SparkSession with Hadoop OAuth config
spark = SparkSession.builder.appName("NetflixStreamingJob").getOrCreate()

spark.conf.set(f"spark.hadoop.fs.azure.account.auth.type.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", "OAuth")
spark.conf.set(f"spark.hadoop.fs.azure.account.oauth.provider.type.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
spark.conf.set(f"spark.hadoop.fs.azure.account.oauth2.client.id.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", AZURE_CLIENT_ID)
spark.conf.set(f"spark.hadoop.fs.azure.account.oauth2.client.secret.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", AZURE_CLIENT_SECRET)
spark.conf.set(f"spark.hadoop.fs.azure.account.oauth2.client.endpoint.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/token")

# Read from Event Hubs via Kafka interface
df_raw = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "spark-eh-ns.servicebus.windows.net:9093") \
    .option("subscribe", "spark-topic") \
    .option("kafka.security.protocol", "SASL_SSL") \
    .option("kafka.sasl.mechanism", "PLAIN") \
    .option("kafka.sasl.jaas.config", f'kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required username="$ConnectionString" password="{EVENT_HUB_CONNECTION_STRING}";') \
    .load()

# Parse the JSON payload
df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# Write to ADLS in Parquet format
query = df_parsed.writeStream \
    .format("parquet") \
    .option("checkpointLocation", checkpoint_path) \
    .option("path", output_path) \
    .outputMode("append") \
    .start()

query.awaitTermination()
