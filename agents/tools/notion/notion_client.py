import os
import requests
import logging
from dotenv import load_dotenv

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
            is_completed = properties.get("Checkbox", {}).get("checkbox", False)

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