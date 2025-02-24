import base64
import json
import requests
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any
from dotenv import load_dotenv

class FitbitAuthenticator:
    """Handles authentication with Fitbit API."""
    
    TOKEN_URL = "https://api.fitbit.com/oauth2/token"
    
    def __init__(self, client_id: str, client_secret: str, credentials_path: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.credentials_path = credentials_path
        self.access_token = None
        self.refresh_token = None
        self._initialize_tokens()
        
    def _initialize_tokens(self) -> None:
        self.access_token, self.refresh_token = self._load_tokens()
        if not self.access_token:
            self._update_access_token()

    def _load_tokens(self) -> Tuple[Optional[str], Optional[str]]:
        try:
            with open(self.credentials_path, "r") as file:
                data = json.load(file)
                return data.get("access_token"), data.get("refresh_token")
        except (FileNotFoundError, json.JSONDecodeError):
            return None, None

    def _save_tokens(self) -> None:
        data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token
        }
        with open(self.credentials_path, "w") as file:
            json.dump(data, file, indent=2)

    def _get_auth_header(self) -> Dict[str, str]:
        auth_string = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        return {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def _update_access_token(self) -> bool:
        if not self.refresh_token:
            return False

        response = requests.post(
            self.TOKEN_URL,
            headers=self._get_auth_header(),
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }
        )

        if response.status_code != 200:
            return False

        tokens = response.json()
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]
        self._save_tokens()
        return True

    def get_auth_header(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}