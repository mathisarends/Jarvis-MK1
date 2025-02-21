import requests
import datetime
import base64
import os
import json
import logging
from dotenv import load_dotenv
from typing import Tuple, Optional, Dict, Any

class FitbitAPI:
    """Class to interact with the Fitbit API."""
    
    TOKEN_URL = "https://api.fitbit.com/oauth2/token"
    BASE_URL = "https://api.fitbit.com/1.2/user/-"
    
    def __init__(self):
        """Initialize the FitbitAPI with credentials and tokens."""
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize credentials and tokens
        self._setup_credentials()
        self._initialize_tokens()
        
    def _setup_credentials(self) -> None:
        """Set up client credentials from environment variables."""
        load_dotenv()
        self.client_id = os.getenv("FITBIT_CLIENT_ID")
        self.client_secret = os.getenv("FITBIT_CLIENT_SECRET")
        self.credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
        
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Missing Fitbit API credentials in environment variables")

    def _initialize_tokens(self) -> None:
        """Initialize access and refresh tokens."""
        self.access_token, self.refresh_token = self._load_tokens()
        if not self.access_token:
            self._update_access_token()

    def _load_tokens(self) -> Tuple[Optional[str], Optional[str]]:
        """Load tokens from credentials file."""
        try:
            with open(self.credentials_path, "r") as file:
                data = json.load(file)
                return data.get("access_token"), data.get("refresh_token")
        except (FileNotFoundError, json.JSONDecodeError):
            self.logger.warning("credentials.json not found or invalid")
            return None, None

    def _save_tokens(self) -> None:
        """Save current tokens to credentials file."""
        data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token
        }
        with open(self.credentials_path, "w") as file:
            json.dump(data, file, indent=2)
        self.logger.debug("Tokens saved to credentials.json")

    def _get_auth_header(self) -> Dict[str, str]:
        """Generate authorization header for API requests."""
        auth_string = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        return {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def _update_access_token(self) -> bool:
        """Update access token using refresh token."""
        if not self.refresh_token:
            self.logger.error("No valid refresh token available")
            return False

        response = requests.post(
            self.TOKEN_URL,
            headers=self._get_auth_header(),
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }
        )

        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]
            self._save_tokens()
            self.logger.info("Access token successfully renewed")
            return True
        
        self.logger.error(f"Failed to renew access token: {response.json()}")
        return False

    def make_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make an authenticated request to the Fitbit API."""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        response = requests.get(url, headers=headers)
        
        if response.status_code == 401:
            self.logger.info("Token expired, attempting renewal")
            if self._update_access_token():
                headers["Authorization"] = f"Bearer {self.access_token}"
                response = requests.get(url, headers=headers)
            else:
                return None

        if response.status_code == 200:
            return response.json()
        
        self.logger.error(f"API request failed: {response.json()}")
        return None

    def get_sleep_data(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get sleep data for a specific date.
        
        Args:
            date (str, optional): Date in format YYYY-MM-DD. Defaults to today.
        """
        date = date or datetime.date.today().strftime("%Y-%m-%d")
        endpoint = f"/sleep/date/{date}.json"
        
        sleep_data = self.make_request(endpoint)
        return sleep_data.get("summary") if sleep_data else None

    def request_new_access_token(self, auth_code: str) -> bool:
        """
        Request a new access token using an authorization code.
        https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=CLIENT_ID&redirect_uri=http://localhost&scope=sleep&expires_in=604800
        """
        response = requests.post(
            self.TOKEN_URL,
            headers=self._get_auth_header(),
            data={
                "client_id": self.client_id,
                "grant_type": "authorization_code",
                "redirect_uri": "https://example.com/redirect",
                "code": auth_code
            }
        )

        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]
            self._save_tokens()
            self.logger.info("New access token successfully obtained")
            return True
            
        self.logger.error(f"Failed to obtain new access token: {response.json()}")
        return False