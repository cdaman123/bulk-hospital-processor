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

If you haven't already installed Poetry, install it first: `pip install poetry`

**Quick Start**
You can set up and run the project locally with these commands:

```bash
# Set up environment variables
cp .env.example .env

# Install dependencies and activate the environment
make install
poetry shell

# Initialize database and run
make db-upgrade
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

