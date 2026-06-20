import logging
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.exceptions import ExternalAPIError

logger = logging.getLogger(__name__)


class HospitalDirectoryClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        # We use a default timeout of 10s
        self.timeout = httpx.Timeout(10.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True,
    )
    def create_hospital(
        self, name: str, address: str, phone: str | None, batch_id: str
    ) -> dict[str, Any]:
        """Create a hospital and return the created hospital data."""
        url = f"{self.base_url}/hospitals/"
        payload = {"name": name, "address": address, "creation_batch_id": batch_id}
        if phone:
            payload["phone"] = phone

        with httpx.Client(timeout=self.timeout) as client:
            try:
                response = client.post(url, json=payload)
                response.raise_for_status()
                return response.json()  # type: ignore
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP error {e.response.status_code} "
                    f"creating hospital: {e.response.text}"
                )
                raise ExternalAPIError(
                    f"API Error: {e.response.status_code}",
                    status_code=e.response.status_code,
                    response_body=e.response.text,
                )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True,
    )
    def activate_batch(self, batch_id: str) -> None:
        """Activate all hospitals in a batch."""
        url = f"{self.base_url}/hospitals/batch/{batch_id}/activate"
        with httpx.Client(timeout=self.timeout) as client:
            try:
                response = client.patch(url)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP error {e.response.status_code} "
                    f"activating batch {batch_id}: {e.response.text}"
                )
                raise ExternalAPIError(
                    f"API Error: {e.response.status_code}",
                    status_code=e.response.status_code,
                    response_body=e.response.text,
                )
