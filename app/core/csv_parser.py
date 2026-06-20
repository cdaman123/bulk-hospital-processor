import csv
import io
from dataclasses import dataclass
from typing import IO

from app.core.exceptions import CSVValidationError


@dataclass
class HospitalRow:
    row_number: int
    name: str
    address: str
    phone: str | None = None


class CSVParser:
    def __init__(self, max_rows: int = 20):
        self.max_rows = max_rows
        self.required_columns = {"name", "address"}

    def parse(self, file_stream: IO[bytes]) -> list[HospitalRow]:
        try:
            # Read and decode the stream
            content = file_stream.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            raise CSVValidationError("File is not a valid UTF-8 CSV.")

        if not content.strip():
            raise CSVValidationError("CSV file is empty.")

        reader = csv.DictReader(io.StringIO(content))
        if not reader.fieldnames:
            raise CSVValidationError("CSV file has no headers.")

        headers = {h.strip().lower() for h in reader.fieldnames if h}

        missing_columns = self.required_columns - headers
        if missing_columns:
            raise CSVValidationError(
                f"Missing required columns: {', '.join(missing_columns)}"
            )

        rows = []
        for i, row in enumerate(reader, start=1):
            if i > self.max_rows:
                raise CSVValidationError(
                    f"CSV exceeds maximum allowed rows ({self.max_rows})."
                )

            # Clean keys to lowercase and strip whitespace
            clean_row = {
                k.strip().lower(): v.strip() if v else None for k, v in row.items() if k
            }

            name = clean_row.get("name")
            address = clean_row.get("address")
            phone = clean_row.get("phone")

            if not name:
                raise CSVValidationError("Name is required.", row=i)
            if not address:
                raise CSVValidationError("Address is required.", row=i)

            rows.append(
                HospitalRow(row_number=i, name=name, address=address, phone=phone)
            )

        if not rows:
            raise CSVValidationError("CSV file contains no data rows.")

        return rows
