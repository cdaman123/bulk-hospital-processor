class BulkProcessorError(Exception):
    """Base exception for bulk processor."""
    pass

class CSVValidationError(BulkProcessorError):
    def __init__(self, message: str, row: int | None = None, errors: dict | list | None = None):
        super().__init__(message)
        self.row = row
        self.errors = errors

class ExternalAPIError(BulkProcessorError):
    def __init__(self, message: str, status_code: int | None = None, response_body: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

class BatchProcessingError(BulkProcessorError):
    pass
