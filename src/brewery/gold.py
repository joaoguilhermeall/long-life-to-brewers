import logging

from pyspark.sql import DataFrame, SparkSession

from brewery.common import BreweryConfig, get_version

_logger = logging.getLogger(__name__)


class BreweryGold:
    def __init__(self, config: BreweryConfig):
        self._config = config

    def _aggregate_data(self, df: DataFrame) -> dict[str, DataFrame]:
        # Example aggregation: Group by 'brewery_type' and count the number of breweries
        return {
            "per_type": df.groupBy("brewery_type").count(),
            "per_country": df.groupBy("country").count(),
        }

    def _write_data(self, spark: SparkSession, df: DataFrame, sulffix: str, output_path: str) -> None:
        _logger.info(f"Writing data to table {self._config.gold_table_name}_{sulffix}")
        table_name = f"{self._config.gold_table_name}_{sulffix}"
        if not spark.catalog.tableExists(table_name):
            _logger.info(f"Creating table {table_name}")

            (
                spark.createDataFrame([], df.schema)
                .writeTo(table_name)
                .using("iceberg")
                .tableProperty("format-version", "2")  # 2 is the default only for Iceberg >= 1.4.0
                .tableProperty("brewery-pipeline.version", get_version())
                .tableProperty("location", f"{output_path}/{table_name}")
                .tableProperty("write.distribution-mode", "hash")
                .create()
            )

        # Alguma coisa não tá funcionando com o Rest Catalog
        df.writeTo(table_name).using("iceberg").overwritePartitions()
        _logger.info(f"Data written to table {table_name} in {output_path}/{table_name}")

    def run(self):
        _logger.info("Starting Brewery Gold Transformation Job")
        _logger.info("Starting Spark Session")
        spark = SparkSession.builder.appName("Brewery Data Pipeline").getOrCreate()
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {self._config.db_name}")
        spark.sql(f"USE {self._config.db_name}")

        output_path = f"s3a://{self._config.minio_bucket_name}/{self._config.gold_path}"

        silver_table = f"{self._config.db_name}.{self._config.silver_table_name}"
        _logger.info(f"Reading silver table {silver_table}")

        if not spark.catalog.tableExists(silver_table):
            _logger.error(f"Silver table {silver_table} does not exist.")
            raise ValueError(f"Silver table {silver_table} does not exist.")

        df_silver = spark.table(silver_table).cache()

        for suffix, df in self._aggregate_data(df_silver).items():
            self._write_data(spark, df, suffix, output_path)

        _logger.info("Brewery Gold Transformation Job completed successfully")
