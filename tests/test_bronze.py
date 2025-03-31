import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from brewery.bronze import BreweryBronze, RequestExecutor
from brewery.exceptions import (
    OpenBreweryDBGetDataException,
    RequestExecutorError,
    StorageSaveFileError,
)


@pytest.fixture
def mock_storage_client(mocker, mock_config):
    storage_client = mocker.patch("brewery.bronze.MinioStorageClient", autospec=True)
    return storage_client(mock_config)


@pytest.fixture
def mock_open_brewery_client(mocker, mock_config):
    client = mocker.patch("brewery.bronze.OpenBreweryDBClient", autospec=True)
    return client(mock_config)


@pytest.fixture
def bronze_instance(mock_config, mock_storage_client, mock_open_brewery_client):
    bronze = BreweryBronze(mock_config)
    bronze._storage_client = mock_storage_client
    bronze._open_brewery_db_client = mock_open_brewery_client
    return bronze


def test_bronze_run_success(mocker, bronze_instance):
    mocker.patch("brewery.bronze.TemporaryDirectory", return_value=MagicMock())
    bronze_instance._open_brewery_db_client.extract_data = AsyncMock(
        return_value=[Path("file1.txt"), Path("file2.txt")]
    )
    bronze_instance._storage_client.delete_dir = MagicMock()
    bronze_instance._storage_client.save_file = MagicMock()

    asyncio.run(bronze_instance.run())

    bronze_instance._open_brewery_db_client.extract_data.assert_called_once()
    bronze_instance._storage_client.delete_dir.assert_called_once_with(bronze_instance._config.bronze_path)
    assert bronze_instance._storage_client.save_file.call_count == 2


def test_bronze_run_with_storage_error(mocker, bronze_instance):
    mocker.patch("brewery.bronze.TemporaryDirectory", return_value=MagicMock())
    bronze_instance._open_brewery_db_client.extract_data = AsyncMock(return_value=[Path("file1.txt")])
    bronze_instance._storage_client.save_file = MagicMock(
        side_effect=StorageSaveFileError("file1.txt", "error")
    )

    with pytest.raises(StorageSaveFileError):
        asyncio.run(bronze_instance.run())


async def test_open_brewery_client_get_total_breweries(mocker, mock_open_brewery_client):
    mock_open_brewery_client.get_total_breweries = AsyncMock(return_value=100)

    total_breweries = await mock_open_brewery_client.get_total_breweries()
    assert total_breweries == 100


async def test_open_brewery_client_get_total_breweries_error(mocker, mock_open_brewery_client):
    mock_open_brewery_client.get_total_breweries = AsyncMock(
        side_effect=OpenBreweryDBGetDataException("error")
    )

    with pytest.raises(OpenBreweryDBGetDataException):
        await mock_open_brewery_client.get_total_breweries()


def test_request_executor_run_success(mocker):
    mock_data_dir = MagicMock()

    mock_data_dir.exists = MagicMock(return_value=True)
    mock_data_dir.is_dir = MagicMock(return_value=True)

    mock_get_page = MagicMock(side_effect=[1, 2, None])
    executor = RequestExecutor(1, mock_data_dir, mock_get_page)

    mock_response = MagicMock()
    mock_response.text = "data"
    mock_response.status_code = 200
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    result = asyncio.run(executor.run())
    assert result.is_success


async def test_request_executor_run_with_error(mocker):
    mock_data_dir = AsyncMock()
    mock_data_dir.exists = MagicMock(return_value=True)
    mock_data_dir.is_dir = MagicMock(return_value=True)

    mock_get_page = MagicMock(side_effect=[1, None])
    executor = RequestExecutor(1, mock_data_dir, mock_get_page)
    executor.run = AsyncMock(side_effect=RequestExecutorError("error"))

    mocker.patch("httpx.AsyncClient.get", side_effect=RequestExecutorError("Request failed"))

    with pytest.raises(RequestExecutorError):
        await executor.run()
