import time
import uuid
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import IO

from app.core.csv_parser import CSVParser
from app.core.hospital_client import HospitalDirectoryClient
from app.repositories.batch_repository import BatchRepository
from app.models.batch import Batch, BatchHospitalResult
from app.core.exceptions import CSVValidationError, ExternalAPIError

logger = logging.getLogger(__name__)

class BatchProcessor:
    def __init__(
        self,
        csv_parser: CSVParser,
        client: HospitalDirectoryClient,
        repository: BatchRepository,
        max_concurrent_requests: int = 10
    ):
        self.csv_parser = csv_parser
        self.client = client
        self.repository = repository
        self.max_concurrent_requests = max_concurrent_requests

    def process_bulk_upload(self, file_stream: IO[bytes]) -> dict:
        start_time = time.time()
        
        # 1. Parse and validate CSV
        try:
            rows = self.csv_parser.parse(file_stream)
        except CSVValidationError as e:
            # We don't create a batch in DB if initial CSV parsing fails
            raise e

        # 2. Generate batch ID and initial DB record
        batch_id = str(uuid.uuid4())
        batch = Batch(
            id=batch_id,
            total_hospitals=len(rows),
            processed_hospitals=0,
            failed_hospitals=0,
            batch_activated=False
        )
        self.repository.create_batch(batch)

        # 3. Process each row concurrently
        results = []
        all_success = True
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
            future_to_row = {
                executor.submit(self._create_hospital, row, batch_id): row 
                for row in rows
            }
            
            for future in as_completed(future_to_row):
                row_data = future_to_row[future]
                try:
                    result = future.result()
                    results.append(result)
                    if result.status == "failed":
                        all_success = False
                        batch.failed_hospitals += 1
                    else:
                        batch.processed_hospitals += 1
                except Exception as exc:
                    logger.exception(f"Row {row_data.row_number} generated an exception: {exc}")
                    all_success = False
                    batch.failed_hospitals += 1
                    results.append(BatchHospitalResult(
                        batch_id=batch_id,
                        row=row_data.row_number,
                        name=row_data.name,
                        status="failed",
                        error_detail="Internal processing error"
                    ))

        # Save results to db
        self.repository.add_results(results)

        # 4. If all succeeded, activate the batch
        if all_success and batch.processed_hospitals == batch.total_hospitals:
            try:
                self.client.activate_batch(batch_id)
                batch.batch_activated = True
                for result in results:
                    result.status = "created_and_activated"
            except ExternalAPIError as e:
                logger.error(f"Failed to activate batch {batch_id}: {e}")
                # We do not fail the overall request, just mark activation as failed
                batch.batch_activated = False

        batch.processing_time_seconds = round(time.time() - start_time, 2)
        self.repository.update_batch(batch)

        # 5. Return summary
        return {
            "batch_id": batch.id,
            "total_hospitals": batch.total_hospitals,
            "processed_hospitals": batch.processed_hospitals,
            "failed_hospitals": batch.failed_hospitals,
            "processing_time_seconds": batch.processing_time_seconds,
            "batch_activated": batch.batch_activated,
            "hospitals": [
                {
                    "row": r.row,
                    "hospital_id": r.hospital_id,
                    "name": r.name,
                    "status": r.status,
                    "error_detail": r.error_detail
                } for r in sorted(results, key=lambda x: x.row)
            ]
        }

    def _create_hospital(self, row, batch_id: str) -> BatchHospitalResult:
        try:
            response_data = self.client.create_hospital(
                name=row.name,
                address=row.address,
                phone=row.phone,
                batch_id=batch_id
            )
            return BatchHospitalResult(
                batch_id=batch_id,
                row=row.row_number,
                hospital_id=response_data.get("id"),
                name=row.name,
                status="created"
            )
        except ExternalAPIError as e:
            return BatchHospitalResult(
                batch_id=batch_id,
                row=row.row_number,
                name=row.name,
                status="failed",
                error_detail=f"API Error: {e.status_code}"
            )
        except Exception as e:
            logger.exception(f"Unexpected error creating hospital for row {row.row_number}")
            return BatchHospitalResult(
                batch_id=batch_id,
                row=row.row_number,
                name=row.name,
                status="failed",
                error_detail=str(e)
            )
