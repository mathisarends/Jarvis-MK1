from agents.tools.notion.core.abstract_notion_client import AbstractNotionClient


class NotionTodoManager(AbstractNotionClient):
    
    def __init__(self, database_id="1a1389d5-7bd3-80b7-9980-ca8ebd734ce2"):
        super().__init__()
        self.database_id = database_id
    
    def get_entries_and_delete_completed(self):
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
        for entry in entries:
            properties = entry["properties"]
            page_id = entry["id"]
            is_completed = properties.get("Kontrollkästchen", {}).get("checkbox", False)

            if is_completed:
                self.delete_page(page_id)
                continue

            title_property = properties["Idee"]["title"]
            title = title_property[0]["text"]["content"] if title_property else "Unnamed Entry"
            status = properties["Status"]["status"]["name"] if "Status" in properties else "No Status"
            priority = properties["Priorität"]["select"]["name"] if "Priorität" in properties and properties["Priorität"]["select"] else "No Priority"

            formatted_entries.append(f"- {title} (Status: {status} | Priority: {priority})")

        return "\nDatabase Entries:\n" + "\n".join(formatted_entries)

    # Das hier parallelisieren wäre auch cool
    def delete_page(self, page_id):
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