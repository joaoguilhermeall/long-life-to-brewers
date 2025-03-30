import pytest

from brewery.common import BreweryConfig, _get_env
from brewery.exceptions import RequiredEnvironmentVariableError


def test_get_env_with_existing_variable(monkeypatch):
    monkeypatch.setenv("TEST_ENV_VAR", "test_value")
    assert _get_env("TEST_ENV_VAR") == "test_value"


def test_get_env_with_default_value(monkeypatch):
    assert _get_env("NON_EXISTENT_ENV_VAR", "default_value") == "default_value"


def test_get_env_raises_error(monkeypatch):
    with pytest.raises(RequiredEnvironmentVariableError):
        _get_env("NON_EXISTENT_ENV_VAR")


def test_brewery_config(monkeypatch):
    monkeypatch.setenv("BREWERY_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("BREWERY_MINIO_ENDPOINT", "localhost:9000")
    monkeypatch.setenv("BREWERY_MINIO_ACCESS_KEY", "access_key")
    monkeypatch.setenv("BREWERY_MINIO_SECRET_KEY", "secret_key")
    monkeypatch.setenv("BREWERY_MINIO_BUCKET_NAME", "bucket_name")
    monkeypatch.setenv("BREWERY_MINIO_SECURE", "0")
    monkeypatch.setenv("BREWERY_EXTRACT_NUM_PARALLEL_TASKS", "5")

    config = BreweryConfig()

    assert config.log_level == "DEBUG"
    assert config.minio_endpoint == "localhost:9000"
    assert config.minio_access_key == "access_key"
    assert config.minio_secret_key == "secret_key"
    assert config.minio_bucket_name == "bucket_name"
    assert config.minio_secure is False
    assert config.extract_num_parallel_tasks == 5
