import importlib.metadata
import os
from pathlib import Path

from brewery.exceptions import RequiredEnvironmentVariableError


def _get_env(key: str, default: str | None = None) -> str:
    """Get the environment variable or return the default value."""
    value = os.environ.get(key, None)

    if value is not None:
        return value.strip()

    elif default is not None:  # "" is accepted as a default value
        return default

    raise RequiredEnvironmentVariableError(key)


def get_version():
    return importlib.metadata.version("brewery")


class BreweryConfig:
    def __init__(self):
        # Logging
        self.log_level: str = _get_env("BREWERY_LOG_LEVEL", "INFO")
        self.log_format: str = _get_env(
            "BREWERY_LOG_FORMAT", "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        self.log_file: str = _get_env("BREWERY_LOG_FILE", "brewery.log")

        # Minio
        self.minio_endpoint: str = _get_env("BREWERY_MINIO_ENDPOINT", "localhost:9000")
        self.minio_access_key: str = _get_env("BREWERY_MINIO_ACCESS_KEY", "minio")
        self.minio_secret_key: str = _get_env("BREWERY_MINIO_SECRET_KEY")
        self.minio_bucket_name: str = _get_env("BREWERY_MINIO_BUCKET_NAME", "breweries-data")
        self.minio_secure: bool = bool(int(_get_env("BREWERY_MINIO_SECURE", "0")))

        os.environ["AWS_ACCESS_KEY_ID"] = self.minio_access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = self.minio_secret_key
        os.environ["AWS_REGION"] = "us-east-1"

        # Parallelism
        self.extract_num_parallel_tasks: int = int(_get_env("BREWERY_EXTRACT_NUM_PARALLEL_TASKS", "10"))

        self.db_name: str = _get_env("BREWERY_DB_NAME", "brewery.db_all_brewery")

        # bronze
        self.bronze_path: Path = Path(_get_env("BREWERY_BRONZE_PATH", "bronze"))
        self.bronze_overwrite: bool = bool(int(_get_env("BREWERY_BRONZE_OVERWRITE", "1")))

        # silver
        self.silver_table_name: str = _get_env("BREWERY_SILVER_TABLE_NAME", "silver_brewery")
        self.silver_path: Path = Path(_get_env("BREWERY_SILVER_PATH", "silver"))

        # gold
        self.gold_table_name: str = _get_env("BREWERY_GOLD_TABLE_NAME", "gold_brewery")
        self.gold_path: Path = Path(_get_env("BREWERY_GOLD_PATH", "gold"))
