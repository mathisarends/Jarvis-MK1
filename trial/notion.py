import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_SECRET")
PAGE_ID = "19c389d57bd380dbb009efe9e5937399"


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

DATABASE_ID = "1a1389d5-7bd3-80b7-9980-ca8ebd734ce2" 

def get_database_entries_and_delete_completed():
    """Listet alle Einträge aus einer Notion-Datenbank auf und löscht die, die bereits erledigt sind (Kontrollkästchen=True)."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    response = requests.post(url, headers=HEADERS)
    
    if response.status_code == 200:
        entries = response.json()["results"]

        if not entries:
            print("ℹ️ Keine Einträge in der Datenbank gefunden.")
            return
        
        print("\n📌 **Datenbank-Einträge:**")
        for entry in entries:
            properties = entry["properties"]
            page_id = entry["id"]  # Die ID des Eintrags zum Löschen

            # Kontrollkästchen-Status abrufen (Standard: False)
            erledigt = properties.get("Kontrollkästchen", {}).get("checkbox", False)
            
            # Wenn der Eintrag als erledigt markiert ist, lösche ihn
            if erledigt:
                delete_page(page_id)
                continue  # Überspringt den gelöschten Eintrag

            # Titel extrahieren
            title_property = properties["Idee"]["title"]
            title = title_property[0]["text"]["content"] if title_property else "Unbenannter Eintrag"

            # Status abrufen
            status = properties["Status"]["status"]["name"] if "Status" in properties else "Kein Status"

            # Priorität abrufen
            priorität = properties["Priorität"]["select"]["name"] if "Priorität" in properties and properties["Priorität"]["select"] else "Keine Priorität"

            print(f"- {title} (Status: {status} | Priorität: {priorität})")
    else:
        print("❌ Fehler beim Abrufen der Einträge:", response.text)


def delete_page(page_id: str):
    """Löscht eine Seite (Eintrag) aus Notion."""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {"archived": True}  # Setzt die Seite auf archiviert (Notion erlaubt kein direktes Löschen)

    response = requests.patch(url, headers=HEADERS, json=data)

    if response.status_code == 200:
        print(f"🗑️ Erfolgreich gelöscht: {page_id}")
    else:
        print(f"❌ Fehler beim Löschen von {page_id}: {response.text}")


# Test ausführen
get_database_entries_and_delete_completed()

def add_database_entry(idea: str):
    """Fügt einen neuen Eintrag zur Notion-Datenbank hinzu."""
    url = "https://api.notion.com/v1/pages"
    status = "Neu"
    priority = "Mittel"
    
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Idee": {
                "title": [{"text": {"content": f"💡 {idea}"}}]
            },
            "Status": {
                "status": {"name": status}  
            },
            "Priorität": {
                "select": {"name": priority}  
            }
        }
    }
    
    response = requests.post(url, headers=HEADERS, json=data)
    
    if response.status_code == 200:
        print(f"✅ Erfolgreich! Der Eintrag '{idea}' wurde hinzugefügt.")
    else:
        print("❌ Fehler beim Hinzufügen des Eintrags:", response.text)
