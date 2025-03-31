import logging

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, trim
from pyspark.sql.types import StringType, StructField, StructType

from brewery.common import BreweryConfig, get_version

_logger = logging.getLogger(__name__)

schema = StructType(
    [
        StructField("id", StringType(), True),
        StructField("name", StringType(), True),
        StructField("brewery_type", StringType(), True),
        StructField("address_1", StringType(), True),
        StructField("address_2", StringType(), True),
        StructField("address_3", StringType(), True),
        StructField("city", StringType(), True),
        StructField("state_province", StringType(), True),
        StructField("postal_code", StringType(), True),
        StructField("country", StringType(), True),
        StructField("longitude", StringType(), True),
        StructField("latitude", StringType(), True),
        StructField("phone", StringType(), True),
        StructField("website_url", StringType(), True),
        StructField("state", StringType(), True),
        StructField("street", StringType(), True),
    ]
)


class BrewerySilver:
    def __init__(self, config: BreweryConfig):
        self._config = config

    def _apply_transformations(self, df: DataFrame) -> DataFrame:
        for col_name in [field.name for field in schema.fields if isinstance(field.dataType, StringType)]:
            df = df.withColumn(col_name, trim(col(col_name)))

        # Convert longitude and latitude to DoubleType and handle invalid values
        df = df.withColumn("longitude", col("longitude").cast("double")).withColumn(
            "latitude", col("latitude").cast("double")
        )

        # Drop duplicates based on the 'id' column
        df = df.dropDuplicates(["id"])

        return df

    def _write_data(self, spark: SparkSession, df_silver: DataFrame, output_path: str) -> None:
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {self._config.db_name}")
        spark.sql(f"USE {self._config.db_name}")

        if not spark.catalog.tableExists(self._config.silver_table_name):
            _logger.info(f"Creating table {self._config.silver_table_name}")

            (
                spark.createDataFrame([], df_silver.schema)
                .writeTo(self._config.silver_table_name)
                .using("iceberg")
                .tableProperty("format-version", "2")  # 2 is the default only for Iceberg >= 1.4.0
                .tableProperty("brewery-pipeline.version", get_version())
                .tableProperty("location", f"{output_path}/{self._config.silver_table_name}")
                .create()
            )
            spark.sql(
                f"ALTER TABLE {self._config.silver_table_name} WRITE DISTRIBUTED BY PARTITION LOCALLY "
                "ORDERED BY country"
            )

        # Alguma coisa não tá funcionando com o Rest Catalog
        df_silver.writeTo(self._config.silver_table_name).using("iceberg").overwritePartitions()

    def run(self):
        _logger.info("Starting Brewery Silver Transformation Job")
        _logger.info("Starting Spark Session")
        spark = SparkSession.builder.appName("Brewery Data Pipeline").getOrCreate()

        input_path = f"s3a://{self._config.minio_bucket_name}/{self._config.bronze_path}/breweries"
        output_path = f"s3a://{self._config.minio_bucket_name}/{self._config.silver_path}"

        _logger.info(f"Reading data from {input_path}")
        df_bronze = spark.read.format("json").schema(schema).load(input_path).cache()

        _logger.info("Transforming data")
        df_silver = self._apply_transformations(df_bronze)

        self._write_data(spark, df_silver, output_path)
        _logger.info(f"Silver data written to table {self._config.silver_table_name} in {output_path}")

        spark.stop()
        _logger.info("Spark Session stopped")
        _logger.info("Brewery Silver Transformation Job completed successfully")
