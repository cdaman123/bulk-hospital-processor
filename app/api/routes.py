import traceback
from typing import Any

from flask import Response, current_app, jsonify, request
from flask_smorest import Blueprint, abort
from werkzeug.exceptions import HTTPException

from app.api.schemas import BulkProcessResponseSchema, ErrorSchema, FileUploadSchema
from app.core.batch_processor import BatchProcessor
from app.core.csv_parser import CSVParser
from app.core.exceptions import BulkProcessorError, CSVValidationError
from app.core.hospital_client import HospitalDirectoryClient
from app.repositories.batch_repository import BatchRepository

bp = Blueprint("api", __name__, description="Operations on hospitals")


@bp.errorhandler(CSVValidationError)  # type: ignore[misc]
def handle_csv_validation_error(e: CSVValidationError) -> tuple[Response, int]:
    return jsonify(
        {
            "error": "CSV Validation Error",
            "message": str(e),
            "row": getattr(e, "row", None),
        }
    ), 400


@bp.errorhandler(BulkProcessorError)  # type: ignore[misc]
def handle_bulk_processor_error(e: BulkProcessorError) -> tuple[Response, int]:
    return jsonify({"error": "Processing Error", "message": str(e)}), 500


@bp.errorhandler(Exception)  # type: ignore[misc]
def handle_general_exception(e: Exception) -> tuple[Response, int] | HTTPException:
    if isinstance(e, HTTPException):
        return e
    current_app.logger.error(f"Unhandled exception: {e}\n{traceback.format_exc()}")
    return jsonify(
        {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred.",
        }
    ), 500


@bp.route("/hospitals/bulk", methods=["POST"])  # type: ignore[misc]
@bp.arguments(FileUploadSchema, location="files")  # type: ignore[misc]
@bp.response(200, BulkProcessResponseSchema)  # type: ignore[misc]
@bp.alt_response(400, schema=ErrorSchema, description="Validation Error")  # type: ignore[misc]
@bp.alt_response(500, schema=ErrorSchema, description="Internal Error")  # type: ignore[misc]
def bulk_process_hospitals(files_data: dict[str, Any]) -> dict[str, Any]:
    """
    Upload and process a bulk CSV file of hospitals.
    Expects a multipart/form-data request with a `file` field containing the CSV.
    """
    file = request.files.get("file")
    if not file or file.filename == "":
        abort(400, message="No file selected for uploading")
    assert file is not None

    if not str(file.filename).endswith(".csv"):
        abort(400, message="File must be a CSV")

    max_rows = current_app.config["MAX_CSV_ROWS"]
    max_concurrent = current_app.config["MAX_CONCURRENT_REQUESTS"]
    api_base_url = current_app.config["HOSPITAL_API_BASE_URL"]

    csv_parser = CSVParser(max_rows=max_rows)
    client = HospitalDirectoryClient(base_url=api_base_url)
    repository = BatchRepository()

    processor = BatchProcessor(
        csv_parser=csv_parser,
        client=client,
        repository=repository,
        max_concurrent_requests=max_concurrent,
    )

    result = processor.process_bulk_upload(file.stream)
    return result
