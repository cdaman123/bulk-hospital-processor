import traceback
from flask import Blueprint, request, jsonify, current_app

from app.core.csv_parser import CSVParser
from app.core.hospital_client import HospitalDirectoryClient
from app.core.batch_processor import BatchProcessor
from app.repositories.batch_repository import BatchRepository
from app.api.schemas import BulkProcessResponseSchema
from app.core.exceptions import CSVValidationError, ExternalAPIError, BulkProcessorError

bp = Blueprint("api", __name__)

@bp.errorhandler(CSVValidationError)
def handle_csv_validation_error(e: CSVValidationError):
    return jsonify({
        "error": "CSV Validation Error",
        "message": str(e),
        "row": e.row
    }), 400

@bp.errorhandler(BulkProcessorError)
def handle_bulk_processor_error(e: BulkProcessorError):
    return jsonify({
        "error": "Processing Error",
        "message": str(e)
    }), 500

@bp.errorhandler(Exception)
def handle_general_exception(e: Exception):
    current_app.logger.error(f"Unhandled exception: {e}\n{traceback.format_exc()}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred."
    }), 500

@bp.route("/hospitals/bulk", methods=["POST"])
def bulk_process_hospitals():
    if "file" not in request.files:
        return jsonify({"error": "Bad Request", "message": "No file part in the request"}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Bad Request", "message": "No file selected for uploading"}), 400

    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Bad Request", "message": "File must be a CSV"}), 400

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
        max_concurrent_requests=max_concurrent
    )

    result = processor.process_bulk_upload(file.stream)
    
    schema = BulkProcessResponseSchema()
    return schema.dump(result), 200
