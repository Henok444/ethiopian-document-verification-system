import json
import requests
from app.core.config import settings


class APIClientError(Exception):
    """Custom exception raised when an API call fails."""
    pass


class VerificationAPIClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.API_URL).rstrip("/")

    def verify_single(self, config_dict: dict, image_name: str, image_bytes: bytes, image_type: str) -> dict:
        """Sends a single document verification request to the backend API."""
        files = {
            "json_file": ("request.json", json.dumps(config_dict), "application/json"),
            "image_file": (image_name, image_bytes, image_type or "image/png"),
        }

        try:
            response = requests.post(
                f"{self.base_url}/verify",
                files=files,
                timeout=120,
            )
        except requests.exceptions.ConnectionError:
            raise APIClientError(f"Cannot connect to API at {self.base_url}. Ensure the FastAPI server is running.")
        except requests.exceptions.Timeout:
            raise APIClientError("The verification request timed out after 120 seconds.")

        if not response.ok:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            raise APIClientError(f"API Error ({response.status_code}): {detail}")

        return response.json()

    def verify_batch(self, config_dict: dict, image_files: list) -> dict:
        """Sends a batch of document images for verification."""
        files = [
            ("json_file", ("request.json", json.dumps(config_dict), "application/json"))
        ]

        for img in image_files:
            files.append(
                ("image_files", (img.name, img.getvalue(), img.type or "image/png"))
            )

        try:
            response = requests.post(
                f"{self.base_url}/verify_batch",
                files=files,
                timeout=300,
            )
        except requests.exceptions.ConnectionError:
            raise APIClientError(f"Cannot connect to API at {self.base_url}. Ensure the FastAPI server is running.")
        except requests.exceptions.Timeout:
            raise APIClientError("The batch verification request timed out.")

        if not response.ok:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            raise APIClientError(f"API Error ({response.status_code}): {detail}")

        return response.json()
