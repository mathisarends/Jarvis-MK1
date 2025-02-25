import concurrent.futures
from agents.tools.notion.core.abstract_notion_client import AbstractNotionClient


class NotionTodoManager(AbstractNotionClient):
    
    def __init__(self, database_id="1a1389d5-7bd3-80b7-9980-ca8ebd734ce2"):
        super().__init__()
        self.database_id = database_id
    
    def get_entries_and_delete_completed(self):
        """Holt alle Einträge aus der To-Do-Datenbank und löscht erledigte Aufgaben parallel."""
        response = self._make_request(
            "post", 
            f"databases/{self.database_id}/query"
        )

        if response.status_code != 200:
            self.logger.error(f"Error retrieving entries: {response.text}")
            return f"Error retrieving entries: {response.text}"

        entries = response.json()["results"]
        if not entries:
            self.logger.info("No entries found in the database.")
            return "No entries found in the database."

        formatted_entries = []
        completed_pages = []  # Liste für erledigte Seiten (zum parallelen Löschen)

        for entry in entries:
            properties = entry["properties"]
            page_id = entry["id"]
            is_completed = properties.get("Kontrollkästchen", {}).get("checkbox", False)

            if is_completed:
                completed_pages.append(page_id)
                continue  # Löschen wird später parallel durchgeführt

            title_property = properties["Idee"]["title"]
            title = title_property[0]["text"]["content"] if title_property else "Unnamed Entry"
            status = properties["Status"]["status"]["name"] if "Status" in properties else "No Status"
            priority = properties["Priorität"]["select"]["name"] if "Priorität" in properties and properties["Priorität"]["select"] else "No Priority"

            formatted_entries.append(f"- {title} (Status: {status} | Priority: {priority})")

        # Parallel erledigte Einträge löschen
        self._delete_pages_concurrently(completed_pages)

        return "\nDatabase Entries:\n" + "\n".join(formatted_entries)

    def _delete_pages_concurrently(self, page_ids):
        """Löscht erledigte Einträge parallel mit ThreadPoolExecutor."""
        if not page_ids:
            return

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  # Max 5 parallele Anfragen
            future_to_page = {executor.submit(self.delete_page, page_id): page_id for page_id in page_ids}

            for future in concurrent.futures.as_completed(future_to_page):
                page_id = future_to_page[future]
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Error deleting page {page_id}: {e}")

    def delete_page(self, page_id):
        """Löscht eine einzelne Notion-Seite."""
        response = self._make_request(
            "patch", 
            f"pages/{page_id}", 
            {"archived": True}
        )

        if response.status_code == 200:
            self.logger.info(f"Successfully deleted page: {page_id}")
        else:
            self.logger.error(f"Error deleting page {page_id}: {response.text}")

    def add_entry(self, idea):
        """Adds a new todo entry to the database."""
        status = "Neu"
        priority = "Mittel"
        
        data = {
            "parent": {"database_id": self.database_id},
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
        
        response = self._make_request("post", "pages", data)
        
        if response.status_code == 200:
            self.logger.info(f"Successfully added entry: {idea}")
            return f"Successfully added entry: {idea}"
        else:
            self.logger.error(f"Error adding entry: {response.text}")
            return f"Error adding entry: {response.text}"
