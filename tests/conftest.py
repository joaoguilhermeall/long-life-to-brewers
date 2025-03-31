from pathlib import Path

import pytest

from brewery.common import BreweryConfig


@pytest.fixture(scope="session")
def mock_config(mocker):
    mock_config = mocker.MagicMock(spec=BreweryConfig)
    mock_config.log_level = "INFO"
    mock_config.log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    mock_config.log_file = "brewery.log"
    mock_config.minio_endpoint = "localhost:9000"
    mock_config.minio_access_key = "minio_access_key"
    mock_config.minio_secret_key = "minio_secret_key"
    mock_config.minio_bucket_name = "test-bucket"
    mock_config.minio_secure = False
    mock_config.extract_num_parallel_tasks = 10
    mock_config.bronze_path = Path("bronze")
    mock_config.bronze_overwrite = True
    mock_config.silver_path = Path("silver")
    mock_config.gold_path = "gold"
    return mock_config
