# Common
class RequiredEnvironmentVariableError(Exception):
    """Exception raised when a required environment variable is not set."""

    def __init__(self, var_name: str):
        super().__init__(f"Required environment variable '{var_name}' is not set.")
        self.var_name = var_name


# Bronze


class InvalidFilePathError(Exception):
    """Exception raised when an invalid file path is provided."""

    def __init__(self, file_path: str):
        super().__init__(f"Invalid file path: {file_path}")
        self.file_path = file_path


class StorageSaveFileError(Exception):
    """Exception raised when there is an error saving a file to storage."""

    def __init__(self, file_path: str, message: str):
        super().__init__(f"Error saving file '{file_path}': {message}")

class StorageDeleteDirError(Exception):
    """Exception raised when there is an error deleting a file from storage."""
    def __init__(self, file_path: str, message: str):
        super().__init__(f"Error deleting file '{file_path}': {message}")


class OpenBreweryDBGetDataException(Exception):
    """Exception raised when there is an error fetching data from OpenBreweryDB."""

    def __init__(self, endpoint: str):
        super().__init__(f"Error fetching data from OpenBreweryDB: {endpoint}")
        self.endpoint = endpoint

class RequestExecutorError(Exception):
    """Exception raised when there is an error in the request executor."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
