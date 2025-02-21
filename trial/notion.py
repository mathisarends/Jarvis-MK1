import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_SECRET")
PAGE_ID = "608a67e42e3a469eb17925e8bf075a33"


HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def list_accessible_databases():
    """Listet alle Notion-Datenbanken auf, auf die die API Zugriff hat."""
    url = "https://api.notion.com/v1/search"
    
    response = requests.post(url, headers=HEADERS, json={"filter": {"value": "database", "property": "object"}})
    
    if response.status_code == 200:
        results = response.json()["results"]
        if not results:
            print("❌ Keine Datenbanken gefunden oder Integration hat keinen Zugriff.")
            return
        
        print("\n📌 **Datenbanken, auf die die API Zugriff hat:**")
        for db in results:
            db_name = db["title"][0]["plain_text"] if db["title"] else "Unbenannte Datenbank"
            db_id = db["id"]
            print(f"- **{db_name}** 🆔 {db_id}")

    else:
        print("❌ Fehler beim Abrufen der Datenbanken:", response.text)

# Test ausführen
list_accessible_databases()

DATABASE_ID = "dc242d1e-94bc-45c9-a330-75b0bf18663a" 

def get_database_details():
    """Holt die Struktur der Notion-Datenbank, um zu sehen, welche Spalten sie hat."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        print("✅ Erfolgreich! Hier sind die Details der Datenbank:\n")
        print(response.json())  # Zeigt alle Eigenschaften der Datenbank
    else:
        print("❌ Fehler beim Abrufen der Datenbank:", response.text)

# Test ausführen
get_database_details()