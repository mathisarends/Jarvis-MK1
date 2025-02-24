import os
from typing import Tuple

from dotenv import load_dotenv

from agents.tools.fitbit.fitbit_activity_client import FitbitActivityClient
from agents.tools.fitbit.fitbit_authenticator import FitbitAuthenticator
from agents.tools.fitbit.fitbit_sleep_client import FitbitSleepClient


class FitbitClientFactory:
    @staticmethod
    def create_clients() -> Tuple[FitbitSleepClient, FitbitActivityClient]:
        load_dotenv()
        client_id = os.getenv("FITBIT_CLIENT_ID")
        client_secret = os.getenv("FITBIT_CLIENT_SECRET")
        
        if not all([client_id, client_secret]):
            raise ValueError("Missing Fitbit API credentials in environment variables")
            
        credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
        authenticator = FitbitAuthenticator(client_id, client_secret, credentials_path)
        
        return (
            FitbitSleepClient(authenticator),
            FitbitActivityClient(authenticator)
        )