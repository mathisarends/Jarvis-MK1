import base64
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Konfiguriere deine Fitbit API Zugangsdaten
CLIENT_ID = os.getenv("FITBIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET")
REDIRECT_URI = "https://example.com/redirect"
TOKEN_URL = "https://api.fitbit.com/oauth2/token"
CREDENTIALS_FILE = "credentials.json"


def get_encoded_auth():
    """Erstellt den Base64-codierten Auth-Header für die Fitbit API."""
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    return base64.b64encode(auth_string.encode()).decode()


def request_access_token(auth_code):
    """Sendet eine Anfrage, um einen Access Token und Refresh Token zu bekommen."""
    headers = {
        "Authorization": f"Basic {get_encoded_auth()}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": CLIENT_ID,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": auth_code
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code == 200:
        tokens = response.json()
        return tokens["access_token"], tokens["refresh_token"]
    else:
        print("Fehler beim Abrufen des Tokens:", response.json())
        return None, None


def save_tokens(access_token, refresh_token):
    """Speichert die Tokens in credentials.json."""
    data = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    with open(CREDENTIALS_FILE, "w") as file:
        json.dump(data, file, indent=2)
    print("Tokens erfolgreich gespeichert in credentials.json")


def main():
    print("Bitte gehe auf diese URL und autorisiere die App:")
    auth_url = f"https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=activity%20sleep%20heartrate%20profile&expires_in=604800"
    print(auth_url)

    auth_code = input("Gib den erhaltenen Authorization Code ein: ").strip()
    if not auth_code:
        print("Kein Code eingegeben. Abbruch.")
        return

    access_token, refresh_token = request_access_token(auth_code)
    if access_token and refresh_token:
        save_tokens(access_token, refresh_token)
    else:
        print("Token-Generierung fehlgeschlagen.")


if __name__ == "__main__":
    main()

