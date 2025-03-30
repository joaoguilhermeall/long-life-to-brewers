import asyncio
import logging
import uuid
from dataclasses import dataclass
from math import ceil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, Generator, Protocol  # noqa: UP035

import httpx
from minio import Minio

from brewery.common import BreweryConfig
from brewery.exceptions import (
    InvalidFilePathError,
    OpenBreweryDBGetDataException,
    RequestExecutorError,
    StorageDeleteDirError,
    StorageSaveFileError,
)

_logger = logging.getLogger(__name__)


class StorageClient(Protocol):
    def __init__(self, config: BreweryConfig) -> None:
        """Initialize the storage client with the given configuration."""
        ...

    def save_file(self, source: Path, target: Path) -> None:
        """Upload or save a file to the storage system.
        Args:
            source (Path): The path to the file to be uploaded.
            target (Path): The target path in the storage system.
        """
        ...

    def delete_dir(self, target: Path) -> None:
        """Delete a directory in the storage system.
        Args:
            target (Path): The path to the directory to be deleted.
        """
        ...


class MinioStorageClient:
    def __init__(self, config: BreweryConfig) -> None:
        """Initialize the Minio storage client with the given configuration."""

        self._config = config

        self._minio_client = Minio(
            endpoint=self._config.minio_endpoint,
            access_key=self._config.minio_access_key,
            secret_key=self._config.minio_secret_key,
            secure=self._config.minio_secure,
        )

    def save_file(self, source: Path, target: Path) -> None:
        if source.is_dir():
            raise InvalidFilePathError(source.as_posix())

        try:
            self._minio_client.fput_object(
                bucket_name=self._config.minio_bucket_name,
                object_name=target.as_posix(),
                file_path=source.as_posix(),
            )

        except Exception as e:
            raise StorageSaveFileError(source.as_posix(), str(e)) from e

    def delete_dir(self, target: Path) -> None:
        """Delete a directory in the Minio storage system."""
        try:
            dir_object = self._minio_client.list_objects(
                bucket_name=self._config.minio_bucket_name,
                prefix=target.as_posix(),
                recursive=False,
            )

            if len(list(dir_object)) == 0:
                _logger.info(f"Directory {target.as_posix()} does not exist in Minio.")
                return

            objects = self._minio_client.list_objects(
                bucket_name=self._config.minio_bucket_name,
                prefix=target.as_posix(),
                recursive=True,
            )

            for obj in objects:
                _logger.debug(f"Deleting object: {obj.object_name}")

                self._minio_client.remove_object(
                    bucket_name=self._config.minio_bucket_name,
                    object_name=obj.object_name or "",
                )

            _logger.info(f"Directory {target.as_posix()} deleted from Minio.")

        except Exception as e:
            raise StorageDeleteDirError(target.as_posix(), str(e)) from e


_REQUEST_INTERVAL = 1
_REQUEST_PAGE_SIZE = 200


@dataclass
class BreweryRequest:
    page: int
    response: httpx.Response | None = None
    exception: Exception | None = None

    async def get_data(self, client: httpx.AsyncClient) -> str | None:
        """Get data from the OpenBreweryDB API."""
        params = {"page": self.page, "per_page": _REQUEST_PAGE_SIZE}

        try:
            response = await client.get(f"{RequestExecutor.base_url}/breweries", params=params)

            if response.status_code != 200:
                raise OpenBreweryDBGetDataException(str(response.url))

            response.raise_for_status()

            self.response = response

            return response.text

        except Exception as e:
            _logger.error(f"Request error: {e}")
            self.error = e


class RequestExecutor:
    base_url = "https://api.openbrewerydb.org/v1"

    def __init__(self, num: int, data_dir: Path, get_page: Callable[[], int | None]) -> None:
        """Initialize the request executor with the given ID."""
        if not data_dir.exists() or not data_dir.is_dir():
            raise InvalidFilePathError(data_dir.as_posix())

        self.num = num
        self.data_dir = data_dir
        self.get_page = get_page
        self.uuid = str(uuid.uuid4())

        self.executor_id = f"{self.num:03d}-{self.uuid}"

        self.data_file = self.data_dir / f"{self.executor_id}.txt"

        self._client = httpx.AsyncClient()
        self._client.headers["User-Agent"] = f"Brewery Client/{self.executor_id}"
        self._client.headers["Content-Type"] = "application/json"
        self._client.headers["Accept"] = "application/json"

        self._request_errors: list[BreweryRequest] = []
        self._requests_executed: int = 0
        self._requests_success: int = 0

    @property
    def is_success(self) -> bool:
        """Check if the request executor has succeeded."""
        return self._requests_executed == self._requests_success

    async def run(self) -> "RequestExecutor":
        """Run the request executor."""

        with self.data_file.open("w") as f:
            while page := self.get_page():
                request = BreweryRequest(page=page)

                data = await request.get_data(self._client)

                if data is None:
                    _logger.error(f"Request failed for page {request.page}: {request.exception}")

                    self._request_errors.append(request)

                else:
                    self._requests_success += 1
                    f.write(data + "\n")

                self._requests_executed += 1

                await asyncio.sleep(_REQUEST_INTERVAL)
                _logger.debug(f"Executor {self.uuid} executed request for page {request.page}")

        await self._client.aclose()

        _logger.debug(f"Executor {self.uuid} completed.")

        return self


class OpenBreweryDBClient:
    base_url = "https://api.openbrewerydb.org/v1"

    def __init__(self, config: BreweryConfig) -> None:
        """Initialize the OpenBreweryDB client with the given configuration."""
        self._config = config

    async def get_total_breweries(self) -> int:
        """Get the total number of breweries from OpenBreweryDB API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/breweries/meta")
            if response.status_code != 200:
                raise OpenBreweryDBGetDataException(str(response.url))

            data = response.json()
            return int(data["total"])

    def _page_iter(self, max_page: int) -> Generator[int, Any, Any]:
        yield from range(1, max_page + 1)

    async def extract_data(self, temp_dir: Path) -> list[Path]:
        """Fetch breweries from OpenBreweryDB API."""

        total_breweries = await self.get_total_breweries()
        _page_iter = self._page_iter(ceil(total_breweries / _REQUEST_PAGE_SIZE))

        _logger.info(f"Total breweries to extract: {total_breweries}")

        running_executores: list[asyncio.Task[RequestExecutor]] = []
        failed_executores: list[asyncio.Task[RequestExecutor]] = []
        completed_executores: list[RequestExecutor] = []

        data_files = []

        for i in range(self._config.extract_num_parallel_tasks):
            executor = RequestExecutor(i, temp_dir, lambda: next(_page_iter, None))

            running_executores.append(asyncio.create_task(executor.run(), name=f"{i}-{executor.uuid}"))

            _logger.info(f"Executor {executor.uuid} started.")

        while True:
            running_executores = [r for r in running_executores if not r.done()]

            if not running_executores:
                _logger.info("All executors have completed.")
                break

            completed, pending = await asyncio.wait(
                running_executores, return_when=asyncio.FIRST_COMPLETED, timeout=60
            )

            if not completed:
                _logger.warning(f"No completed tasks in the current batch. Running tasks: {pending}")
                continue

            for task in completed:
                if task.done() and task.exception():
                    _logger.error(f"Task {task.get_name()} failed: {task.exception()}")
                    failed_executores.append(task)

                    raise RequestExecutorError(
                        f"Task {task.get_name()} failed: {task.exception()}"
                    ) from task.exception()

                executor = task.result()

                if not executor.is_success:
                    _logger.error(f"Executor {executor.uuid} encountered errors: {executor._request_errors}")
                    failed_executores.append(task)
                    continue

                completed_executores.append(executor)

                _logger.info(f"Executor {executor.uuid} completed. Data file: {executor.data_file}")

                data_files.append(executor.data_file)
                running_executores.remove(task)

        return data_files


class BreweryBronze:
    def __init__(self, config: BreweryConfig) -> None:
        self._config = config
        self._storage_client: StorageClient = MinioStorageClient(config)
        self._open_brewery_db_client = OpenBreweryDBClient(config)

    async def run(self) -> None:
        """Run the bronze stage of the pipeline."""
        _logger.info("Starting the bronze stage of the pipeline.")
        _logger.info("Extracting data from OpenBreweryDB.")
        with TemporaryDirectory() as temp_dir:
            _logger.info(f"Temporary directory created: {temp_dir}")

            data_files = await self._open_brewery_db_client.extract_data(Path(temp_dir))
            _logger.info(f"Data files extracted: {data_files}")

            if self._config.bronze_overwrite:
                self._storage_client.delete_dir(self._config.bronze_path)

            # TODO: Improve this to use async
            for data_file in data_files:
                target_path = self._config.bronze_path / data_file.name
                _logger.info(f"Saving file {data_file} to storage at {target_path}")
                self._storage_client.save_file(data_file, target_path)
                _logger.info(f"File {data_file} saved to storage at {target_path}")

        _logger.info("Data files saved to storage.")
        _logger.info("Temporary directory deleted.")
        _logger.info("Bronze stage completed.")
