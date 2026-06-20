import io
from unittest.mock import MagicMock

import pytest

from app.core.batch_processor import BatchProcessor
from app.core.csv_parser import CSVParser
from app.core.exceptions import ExternalAPIError
from app.core.hospital_client import HospitalDirectoryClient
from app.repositories.batch_repository import BatchRepository


@pytest.fixture
def mock_client():
    client = MagicMock(spec=HospitalDirectoryClient)
    client.create_hospital.return_value = {"id": 100}
    return client


@pytest.fixture
def repository(app):
    return BatchRepository()


def test_batch_processor_success(mock_client, repository):
    parser = CSVParser()
    processor = BatchProcessor(parser, mock_client, repository)

    csv_data = b"name,address,phone\nH1,A1,\nH2,A2,P2\n"
    file_stream = io.BytesIO(csv_data)

    result = processor.process_bulk_upload(file_stream)

    assert result["total_hospitals"] == 2
    assert result["processed_hospitals"] == 2
    assert result["failed_hospitals"] == 0
    assert result["batch_activated"] is True

    assert mock_client.create_hospital.call_count == 2
    mock_client.activate_batch.assert_called_once_with(result["batch_id"])


def test_batch_processor_partial_failure(mock_client, repository):
    # Simulate first call fails, second succeeds
    mock_client.create_hospital.side_effect = [
        ExternalAPIError("API Error", 500, ""),
        {"id": 101},
    ]

    parser = CSVParser()
    processor = BatchProcessor(parser, mock_client, repository)

    csv_data = b"name,address,phone\nH1,A1,\nH2,A2,P2\n"
    file_stream = io.BytesIO(csv_data)

    result = processor.process_bulk_upload(file_stream)

    assert result["total_hospitals"] == 2
    assert result["processed_hospitals"] == 1
    assert result["failed_hospitals"] == 1
    assert result["batch_activated"] is False

    # Activation should not be called if there was a failure
    mock_client.activate_batch.assert_not_called()
