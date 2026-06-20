import pytest
import io
from app.core.csv_parser import CSVParser
from app.core.exceptions import CSVValidationError

def test_parse_valid_csv():
    parser = CSVParser(max_rows=20)
    csv_data = b"name,address,phone\nH1,A1,P1\nH2,A2,\n"
    file_stream = io.BytesIO(csv_data)
    
    rows = parser.parse(file_stream)
    assert len(rows) == 2
    assert rows[0].name == "H1"
    assert rows[0].address == "A1"
    assert rows[0].phone == "P1"
    
    assert rows[1].name == "H2"
    assert rows[1].address == "A2"
    assert rows[1].phone is None

def test_parse_missing_required_columns():
    parser = CSVParser()
    csv_data = b"name,phone\nH1,P1\n"
    file_stream = io.BytesIO(csv_data)
    
    with pytest.raises(CSVValidationError) as exc:
        parser.parse(file_stream)
    assert "Missing required columns" in str(exc.value)
    assert "address" in str(exc.value)

def test_parse_missing_data():
    parser = CSVParser()
    csv_data = b"name,address,phone\n,A1,P1\n"
    file_stream = io.BytesIO(csv_data)
    
    with pytest.raises(CSVValidationError) as exc:
        parser.parse(file_stream)
    assert "Name is required" in str(exc.value)
    assert exc.value.row == 1

def test_parse_exceeds_max_rows():
    parser = CSVParser(max_rows=2)
    csv_data = b"name,address,phone\nH1,A1,P1\nH2,A2,\nH3,A3,P3\n"
    file_stream = io.BytesIO(csv_data)
    
    with pytest.raises(CSVValidationError) as exc:
        parser.parse(file_stream)
    assert "exceeds maximum allowed rows" in str(exc.value)
