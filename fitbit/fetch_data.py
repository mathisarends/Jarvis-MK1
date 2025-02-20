import requests
import datetime

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1E3TTQiLCJzdWIiOiI1VE1TR1YiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc2xlIiwiZXhwIjoxNzQwMDY1NTA1LCJpYXQiOjE3NDAwMzY3MDV9.jDdupDvGkwlNNufyhszfLPywsjaHA6zlb_GUmLO3GA0"

def get_sleep_data(access_token):
    """Holt die Schlafdaten vom letzten Tag"""
    today = datetime.date.today().strftime("%Y-%m-%d")
    url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{today}.json"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("❌ Fehler:", response.json())
        return None

# Schlafdaten abrufen
sleep_data = get_sleep_data(ACCESS_TOKEN)
print(sleep_data)
