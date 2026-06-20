# Bulk Hospital Processor

A standalone bulk-processing Flask service that integrates with a Hospital Directory API. It takes a CSV file of hospitals, validates it, and concurrently creates the hospitals in the directory. If all creations succeed, it activates the entire batch.

## Architecture

This project follows a clean architectural pattern:
- **Routes (`app/api/routes.py`)**: Thin presentation layer handling HTTP requests and responses. Uses Marshmallow for serialization.
- **Service (`app/core/batch_processor.py`)**: Core business logic orchestrating the CSV parsing, API calls, and DB persistence. Handles concurrent requests.
- **Client (`app/core/hospital_client.py`)**: Wraps external API calls with retries and exponential backoff using `httpx` and `tenacity`.
- **Repository (`app/repositories/batch_repository.py`)**: Persistence layer abstracting the SQLAlchemy ORM.

## Setup

### Using Docker (Recommended)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Start the services:
   ```bash
   make docker-up
   ```
   This will start the Postgres database and the Flask application on port `8000`.

### Local Development

1. Install Poetry if you haven't already:
   ```bash
   pip install poetry
   ```
2. Install dependencies:
   ```bash
   make install
   ```
3. Activate the virtual environment:
   ```bash
   poetry shell
   ```
4. Set up environment variables in `.env`.
5. Initialize the database:
   ```bash
   make db-upgrade
   ```
6. Run the server:
   ```bash
   make run
   ```

## Usage Example

```bash
curl -X POST http://localhost:8000/hospitals/bulk \
  -F "file=@tests/fixtures/sample.csv"
```

## Running Tests

```bash
make test
```

## Known Limitations & Trade-offs

- **Memory constraints**: Currently loads the whole CSV into memory. Max rows are limited to 20, so this is fine. For huge files, stream parsing should be considered.
- **Database**: Using Postgres via Docker for persistence, but fallback to SQLite is possible via environment variables.

