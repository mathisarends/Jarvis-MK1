import os
import requests
import logging
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from agents.tools.notion.notion_markdown_parser import NotionMarkdownParser

load_dotenv()

class NotionClient:
    NOTION_TOKEN = os.getenv("NOTION_SECRET")
    DATABASE_ID = "1a1389d5-7bd3-80b7-9980-ca8ebd734ce2"

    HEADERS = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger.info("NotionManager initialized.")
        

    def get_database_entries_and_delete_completed(self):
        url = f"https://api.notion.com/v1/databases/{self.DATABASE_ID}/query"
        response = requests.post(url, headers=self.HEADERS)

        if response.status_code != 200:
            self.logger.error("Error retrieving entries: %s", response.text)
            return f"Error retrieving entries: {response.text}"

        entries = response.json()["results"]
        if not entries:
            self.logger.info("No entries found in the database.")
            return "No entries found in the database."

        formatted_entries = []
        for entry in entries:
            properties = entry["properties"]
            page_id = entry["id"]
            is_completed = properties.get("Kontrollkästchen", {}).get("checkbox", False)

            if is_completed:
                self.delete_page(page_id)
                continue

            title_property = properties["Idee"]["title"]
            title = title_property[0]["text"]["content"] if title_property else "Unbenannter Eintrag"
            status = properties["Status"]["status"]["name"] if "Status" in properties else "Kein Status"
            priority = properties["Priorität"]["select"]["name"] if "Priorität" in properties and properties["Priorität"]["select"] else "Keine Priorität"

            formatted_entries.append(f"- {title} (Status: {status} | Priority: {priority})")

        return "\nDatabase Entries:\n" + "\n".join(formatted_entries)

    def delete_page(self, page_id):
        url = f"https://api.notion.com/v1/pages/{page_id}"
        data = {"archived": True}
        response = requests.patch(url, headers=self.HEADERS, json=data)

        if response.status_code == 200:
            self.logger.info("Successfully deleted page: %s", page_id)
        else:
            self.logger.error("Error deleting page %s: %s", page_id, response.text)

    def add_database_entry(self, idea):
        url = "https://api.notion.com/v1/pages"
        status = "Neu"
        priority = "Mittel"
        
        data = {
            "parent": {"database_id": self.DATABASE_ID},
            "properties": {
                "Idee": {
                    "title": [{"text": {"content": idea}}]
                },
                "Status": {
                    "status": {"name": status}  
                },
                "Priorität": {
                    "select": {"name": priority}  
                }
            }
        }
        
        response = requests.post(url, headers=self.HEADERS, json=data)
        
        if response.status_code == 200:
            self.logger.info("Successfully added entry: %s", idea)
        else:
            self.logger.error("Error adding entry: %s", response.text)

    def append_to_clipboard_page(self, text: str) -> str:
        """
        Fügt formatierten Text zur Clipboard-Seite hinzu, mit einem Trenner davor.
        """
        clipboard_page_id = "1a3389d5-7bd3-80d7-a507-e67d1b25822c"
        url = f"https://api.notion.com/v1/blocks/{clipboard_page_id}/children"
        
        divider_block = {
            "type": "divider",
            "divider": {}
        }
        
        content_blocks = NotionMarkdownParser.parse_markdown(text)
        
        data = {
            "children": [divider_block] + content_blocks
        }
        
        response = requests.patch(url, headers=self.HEADERS, json=data)
        
        if response.status_code == 200:
            self.logger.info("Text erfolgreich zur Clipboard Seite hinzugefügt.")
            return "Text erfolgreich zur Clipboard Seite hinzugefügt."
        else:
            self.logger.error(f"Fehler beim Hinzufügen des Textes: {response.text}")
            return f"Fehler beim Hinzufügen des Textes: {response.text}"
        
    def get_accessible_pages(self):
        """Ruft alle Notion-Seiten ab, auf die der aktuelle API-Token Zugriff hat."""
        url = "https://api.notion.com/v1/search"
        response = requests.post(url, headers=self.HEADERS, json={"filter": {"value": "page", "property": "object"}})

        if response.status_code != 200:
            self.logger.error("Fehler beim Abrufen der Seiten: %s", response.text)
            return f"Fehler beim Abrufen der Seiten: {response.text}"

        pages = response.json().get("results", [])
        if not pages:
            return "Es wurden keine zugänglichen Seiten gefunden."

        formatted_pages = []
        for page in pages:
            page_id = page["id"]
            title_property = page.get("properties", {}).get("title", {}).get("title", [])
            title = title_property[0]["text"]["content"] if title_property else "Unbenannte Seite"
            formatted_pages.append(f"- {title} (ID: {page_id})")

        return "\nZugängliche Seiten:\n" + "\n".join(formatted_pages)

            
            
if __name__ == "__main__":
    notion_client = NotionClient()
    
    markdown_text = """# Meine tägliche To-Do Liste

    Heute ist ein produktiver Tag! Ich werde mich auf folgende Aufgaben konzentrieren:

    ## 🛠️ Arbeit
    - **Projekt X abschließen**
    - *Feedback zu Feature Y einholen*
    - `Code-Review` für PR #42 durchführen
    - ~~Altes Dashboard löschen~~

    ## 📚 Lernen
    - **Neues Kapitel in 'Clean Code' lesen**
    - *Python AsyncIO ausprobieren*
    - `Markdown`-Syntax weiter vertiefen
    - [Dokumentation zur Notion API](https://developers.notion.com) durchgehen

    ## 💪 Gesundheit
    - __30 Minuten Krafttraining__
    - ~~Fastfood vermeiden~~
    - *Mehr Wasser trinken*

    Am Ende des Tages reflektiere ich, was gut lief und wo ich mich verbessern kann. 🚀
"""
    
    
    result = notion_client.append_to_clipboard_page(markdown_text)
    print(result)
