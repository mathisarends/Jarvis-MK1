import requests
import base64

# Eigentlich muss man hier auf diese url und dasss dann aus der url parsen https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23Q7M4&redirect_uri=https://example.com/redirect&scope=sleep&expires_in=604800
# dann kriegt man immer den auth code und kann sich einen neuen acces token ziehen

CLIENT_ID = "23Q7M4"
CLIENT_SECRET = "947c845230815506bf6b4995cd093b44"
AUTH_CODE = "74b19343d6937cce13082541592b00a45ffd36e2"

TOKEN_URL = "https://api.fitbit.com/oauth2/token"

# Erstelle den Auth-Header (Basic Authentication)
auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

headers = {
    "Authorization": f"Basic {auth_header}",
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "client_id": CLIENT_ID,
    "grant_type": "authorization_code",
    "redirect_uri": "https://example.com/redirect",
    "code": AUTH_CODE
}

response = requests.post(TOKEN_URL, headers=headers, data=data)

if response.status_code == 200:
    tokens = response.json()
    ACCESS_TOKEN = tokens["access_token"]
    REFRESH_TOKEN = tokens["refresh_token"]
    print("✅ Access Token:", ACCESS_TOKEN)
    print("🔄 Refresh Token:", REFRESH_TOKEN)
else:
    print("❌ Fehler:", response.json())
