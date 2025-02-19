import requests

class LocationFinder:
    """Ermittelt den aktuellen Standort anhand der IP-Adresse."""
    
    @staticmethod
    def get_location():
        """Fragt eine externe API ab, um den Standort basierend auf der IP-Adresse zu erhalten."""
        try:
            response = requests.get("https://ipinfo.io/json")
            data = response.json()
            return data.get("city", "Unbekannt") 
        except requests.RequestException:
            return "Unbekannt"

if __name__ == "__main__":
    location = LocationFinder.get_location()
    print(f"Aktueller Standort: {location}")