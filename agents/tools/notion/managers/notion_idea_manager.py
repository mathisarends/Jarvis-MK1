from datetime import datetime, timezone
from agents.tools.notion.core.abstract_notion_client import AbstractNotionClient

class NotionIdeaManager(AbstractNotionClient):
    """Class for managing ideas in a Notion database."""
    
    def __init__(self, database_id="ea889531-fa77-4e26-9fbf-54d9002eeb91"):
        super().__init__()
        self.database_id = database_id
    
    def add_idea(self, name, thema=None):
        """Adds a new idea to the database with optional category."""
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {
                    "title": [{"text": {"content": name}}]
                },
                "Datum": {
                    "date": {"start": current_date}
                }
            },
            # Sets the Notion standard icon as external URL
            "icon": {
                "type": "external",
                "external": {
                    "url": "https://www.notion.so/icons/document_emoji_orange.svg"
                }
            }
        }

        # Add category (theme) if provided
        if thema:
            data["properties"]["Thema"] = {
                "multi_select": [{"name": thema}]
            }

        response = self._make_request("post", "pages", data)

        if response.status_code == 200:
            self.logger.info(f"Successfully added idea: {name}")
            return "Successfully added idea."
        else:
            self.logger.error(f"Error adding idea: {response.text}")
            return f"Error adding idea: {response.text}"