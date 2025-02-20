import requests
import datetime
import base64
import os
from dotenv import load_dotenv

class FitbitAPI:
    def __init__(self):
        """Liest die .env Datei aus dem Projekt-Root unabhängig von der Ordnerstruktur aus."""
        project_root = self.find_project_root()
        self.env_path = os.path.join(project_root, ".env")
        load_dotenv(self.env_path)

        self.client_id = os.getenv("FITBIT_CLIENT_ID")
        self.client_secret = os.getenv("FITBIT_CLIENT_SECRET")
        self.access_token = os.getenv("FITBIT_ACCESS_TOKEN")
        self.refresh_token = os.getenv("FITBIT_REFRESH_TOKEN")

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

        with open(self.env_path, "r") as file:
            lines = file.readlines()

        with open(self.env_path, "w") as file:
            for line in lines:
                if line.startswith("FITBIT_ACCESS_TOKEN="):
                    file.write(f"FITBIT_ACCESS_TOKEN={self.access_token}\n")
                elif line.startswith("FITBIT_REFRESH_TOKEN="):
                    file.write(f"FITBIT_REFRESH_TOKEN={self.refresh_token}\n")
                else:
                    file.write(line)

        load_dotenv(self.env_path, override=True)
        print("✅ Tokens erfolgreich in .env gespeichert und neu geladen.")

    def make_request(self, endpoint):
        """Sendet eine API-Anfrage und erneuert den Token, falls erforderlich."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{self.base_url}{endpoint}", headers=headers)

        if response.status_code == 401:  
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
        sleep_data =  self.make_request(endpoint)
        if sleep_data and "summary" in sleep_data:
            return sleep_data["summary"]
    
    def find_project_root(self):
        """Sucht nach dem Root-Ordner des Projekts, indem nach typischen Projektdateien gesucht wird."""
        current_dir = os.getcwd()
        while current_dir != os.path.dirname(current_dir):  
            if ".git" in os.listdir(current_dir) or ".env" in os.listdir(current_dir):  
                return current_dir
            current_dir = os.path.dirname(current_dir)  
        return os.getcwd()


if __name__ == "__main__":
    fitbit = FitbitAPI()
    sleep_data = fitbit.get_sleep_data()
    print(sleep_data)
