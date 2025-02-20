import requests
import datetime
import base64
import os
from dotenv import load_dotenv

class FitbitAPI:
    def __init__(self, env_file=".env"):
        """Initialisiert die Fitbit API mit OAuth2-Authentifizierung und lädt Werte aus der .env Datei."""
        load_dotenv()

        self.client_id = os.getenv("FITBIT_CLIENT_ID")
        self.client_secret = os.getenv("FITBIT_CLIENT_SECRET")
        self.access_token = os.getenv("FITBIT_ACCESS_TOKEN")
        self.refresh_token = os.getenv("FITBIT_REFRESH_TOKEN")

        print(f"🔑 Fitbit API initialisiert mit access token: {self.access_token}")

        self.token_url = "https://api.fitbit.com/oauth2/token"
        self.base_url = "https://api.fitbit.com/1.2/user/-"

        # Falls kein Access Token vorhanden ist, direkt erneuern
        if not self.access_token:
            self.update_access_token()

    def update_access_token(self):
        """Erneuert den Access Token mit dem gespeicherten Refresh Token."""
        if not self.refresh_token:
            print("❌ Kein gültiger Refresh Token vorhanden. Bitte neu authentifizieren.")
            return

        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }

        response = requests.post(self.token_url, headers=headers, data=data)

        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]
            self.save_tokens()  # Speichert beide Tokens
            print("🔄 Neuer Access Token und Refresh Token gespeichert.")
        else:
            print("❌ Fehler beim Erneuern des Access Tokens:", response.json())

    def save_tokens(self):
        """Speichert den neuen Access Token und Refresh Token in der .env Datei."""
        with open(self.env_file, "r") as file:
            lines = file.readlines()

        with open(self.env_file, "w") as file:
            for line in lines:
                if line.startswith("FITBIT_ACCESS_TOKEN="):
                    file.write(f"FITBIT_ACCESS_TOKEN={self.access_token}\n")
                elif line.startswith("FITBIT_REFRESH_TOKEN="):
                    file.write(f"FITBIT_REFRESH_TOKEN={self.refresh_token}\n")
                else:
                    file.write(line)

        # Aktualisierte Werte direkt in die Umgebung laden
        load_dotenv(self.env_file, override=True)

    def make_request(self, endpoint):
        """Sendet eine API-Anfrage und erneuert den Token, falls erforderlich."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{self.base_url}{endpoint}", headers=headers)

        if response.status_code == 401:  # Ungültiger Token -> Token erneuern und erneut versuchen
            print("⚠️ Access Token abgelaufen. Erneuere Token...")
            self.update_access_token()
            headers["Authorization"] = f"Bearer {self.access_token}"
            
            response = requests.get(f"{self.base_url}{endpoint}", headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print("❌ API Fehler:", response.json())
            return None

    def get_sleep_data(self, date=None):
        """Holt die Schlafdaten für das angegebene Datum (Standard: Letzte Nacht)."""
        if date is None:
            date = datetime.date.today().strftime("%Y-%m-%d")

        endpoint = f"/sleep/date/{date}.json"
        return self.make_request(endpoint)

if __name__ == "__main__":
    fitbit = FitbitAPI()
    sleep_data = fitbit.get_sleep_data()
    print(sleep_data)
