import datetime
import base64
import os
import json
import logging
import requests
import asyncio
import datetime
import aiohttp
import asyncio
from dotenv import load_dotenv
from typing import Tuple, Optional, Dict, Any

class FitbitClient:
    """Class to interact with the Fitbit API."""
    
    TOKEN_URL = "https://api.fitbit.com/oauth2/token"
    BASE_URL = "https://api.fitbit.com/1.2/user/-"
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize credentials and tokens
        self._setup_credentials()
        self._initialize_tokens()
        
    def _setup_credentials(self) -> None:
        load_dotenv()
        self.client_id = os.getenv("FITBIT_CLIENT_ID")
        self.client_secret = os.getenv("FITBIT_CLIENT_SECRET")
        self.credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
        
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Missing Fitbit API credentials in environment variables")

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
            self.logger.warning("credentials.json not found or invalid")
            return None, None

    def _save_tokens(self) -> None:
        data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token
        }
        with open(self.credentials_path, "w") as file:
            json.dump(data, file, indent=2)
        self.logger.debug("Tokens saved to credentials.json")

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

    async def fetch_sleep_data(self, date: str) -> Optional[Dict[str, Any]]:
        """Fetch raw sleep data for a given date."""
        endpoint = f"{self.BASE_URL}/sleep/date/{date}.json"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                print(f"API request for {date} failed: {await response.text()}")
                return None

    def get_sleep_stages(self, sleep_entry: Dict[str, Any]) -> Dict[str, int]:
        """Extract sleep stages (Deep, Light, REM, Wake) from a sleep entry."""
        stages = sleep_entry.get("levels", {}).get("summary", {})
        return {
            "deep": stages.get("deep", {}).get("minutes", 0),
            "light": stages.get("light", {}).get("minutes", 0),
            "rem": stages.get("rem", {}).get("minutes", 0),
            "wake": stages.get("wake", {}).get("minutes", 0)
        }

    async def get_sleep_summary(self, date: str) -> Optional[Dict[str, Any]]:
        """Fetch structured sleep summary for a specific date."""
        sleep_data = await self.fetch_sleep_data(date)
        if not sleep_data or "sleep" not in sleep_data or not sleep_data["sleep"]:
            return None
        
        main_sleep = sleep_data["sleep"][0]  # Use the primary sleep session
        sleep_stages = self.get_sleep_stages(main_sleep)

        return {
            "date": date,
            "start_time": main_sleep.get("startTime"),
            "end_time": main_sleep.get("endTime"),
            "sleep_duration": main_sleep.get("minutesAsleep", 0),
            "sleep_stages": sleep_stages
        }

    async def get_last_5_days_sleep_summary(self) -> Dict[str, Any]:
        """Fetch sleep summaries for the past 5 days plus today and aggregate the data."""
        today = datetime.date.today()
        dates = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6)]

        sleep_summaries = await asyncio.gather(*[self.get_sleep_summary(date) for date in dates])
        sleep_summaries = [s for s in sleep_summaries if s is not None]  # Remove None values

        total_sleep_time = sum(s["sleep_duration"] for s in sleep_summaries)
        average_sleep_time = total_sleep_time // len(sleep_summaries) if sleep_summaries else 0

        # Durchschnittswerte für Schlafphasen berechnen
        avg_sleep_stages = {
            "deep": sum(s["sleep_stages"]["deep"] for s in sleep_summaries) // len(sleep_summaries) if sleep_summaries else 0,
            "light": sum(s["sleep_stages"]["light"] for s in sleep_summaries) // len(sleep_summaries) if sleep_summaries else 0,
            "rem": sum(s["sleep_stages"]["rem"] for s in sleep_summaries) // len(sleep_summaries) if sleep_summaries else 0,
            "wake": sum(s["sleep_stages"]["wake"] for s in sleep_summaries) // len(sleep_summaries) if sleep_summaries else 0,
        }

        return {
            "total_sleep_time": total_sleep_time,
            "average_sleep_time": average_sleep_time,
            "average_sleep_stages": avg_sleep_stages,
            "sleep_sessions": sleep_summaries
        }


async def main():
    fitbit = FitbitClient()

    today_summary = await fitbit.get_sleep_summary(datetime.date.today().strftime("%Y-%m-%d"))
    last_5_days_summary = await fitbit.get_last_5_days_sleep_summary()

    result = {
        "today": today_summary,
        "last_5_days": last_5_days_summary
    }

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())