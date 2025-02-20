import requests
import datetime
import base64

class FitbitAPI:
    def __init__(self, client_id, client_secret, refresh_token, access_token):
        """Initialisiert die Fitbit API mit OAuth2-Authentifizierung."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.token_url = "https://api.fitbit.com/oauth2/token"
        self.base_url = "https://api.fitbit.com/1.2/user/-"
        self.update_access_token()

    def update_access_token(self):
        """Erneuert den Access Token mit dem Refresh Token."""
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
            print("🔄 Neuer Access Token abgerufen.")
        else:
            print("❌ Fehler beim Erneuern des Access Tokens:", response.json())

    def make_request(self, endpoint):
        """Sendet eine API-Anfrage und erneuert den Token, falls erforderlich."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{self.base_url}{endpoint}", headers=headers)

        if response.status_code == 401: 
            print("⚠️ Access Token abgelaufen. Erneuere Token...")
            self.update_access_token()
            
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
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

# ✅ Beispielhafte Verwendung:
if __name__ == "__main__":
    CLIENT_ID = "23Q7M4"
    CLIENT_SECRET = "947c845230815506bf6b4995cd093b44"
    REFRESH_TOKEN = "74c92cfd0d3cc700904496ab2f23f681f9813cf141be526c19a89bc590a6b79c"
    ACCESS_TOKEN="eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1E3TTQiLCJzdWIiOiI1VE1TR1YiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc2xlIiwiZXhwIjoxNzQwMDY3Mjc2LCJpYXQiOjE3NDAwMzg0NzZ9.QFzL3j6dT7JumEac1l0PRNfRX7SxDMLkCZIl7-1MXyw"

    fitbit = FitbitAPI(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ACCESS_TOKEN)
    sleep_data = fitbit.get_sleep_data()
    print(sleep_data)
