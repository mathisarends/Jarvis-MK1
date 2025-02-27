import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
from agents.tools.notion.core.abstract_notion_client import AbstractNotionClient
from agents.tools.notion.core.notion_pages import NotionPages

class NotionIdeaManager(AbstractNotionClient):

    def __init__(self):
        super().__init__()
        self.database_id = NotionPages.get_database_id("IDEAS")

    def add_idea(self, name, tags=None, status="Initial"):

        data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {
                    "title": [{"text": {"content": name}}]
                },
                "Status": {
                    "status": {"name": status}
                }
            },
            "icon": {
                "type": "external",
                "external": {"url": "https://www.notion.so/icons/document_emoji_orange.svg"}
            }
        }

        # Falls Tags (Mehrfachauswahl) mitgegeben werden
        if tags:
            data["properties"]["Art"] = {
                "multi_select": [{"name": tag} for tag in tags]
            }

        try:
            response = self._make_request("post", "pages", data)

            if response.status_code == 200:
                self.logger.info(f"✅ Successfully added idea: {name}")
                return f"✅ Idea '{name}' added successfully."
            else:
                self.logger.error(f"❌ Error adding idea: {response.text}")
                return f"❌ Error adding idea: {response.text}"

        except Exception as e:
            self.logger.error(f"❌ API call failed: {str(e)}")
            return f"❌ API call failed: {str(e)}"

    def get_all_ideas(self):
        """Retrieves all ideas from the Notion database."""
        try:
            response = self._make_request("post", f"databases/{self.database_id}/query")

            if response.status_code != 200:
                self.logger.error(f"❌ Error retrieving ideas: {response.text}")
                return f"❌ Error retrieving ideas: {response.text}"

            results = response.json().get("results", [])
            ideas = [
                {
                    "id": item["id"],
                    "name": item["properties"]["Name"]["title"][0]["text"]["content"],
                    "status": item["properties"]["Status"]["status"]["name"],
                    "tags": [tag["name"] for tag in item["properties"].get("Art", {}).get("multi_select", [])]
                }
                for item in results
            ]

            return ideas

        except Exception as e:
            self.logger.error(f"❌ API call failed: {str(e)}")
            return f"❌ API call failed: {str(e)}"


if __name__ == "__main__":
    manager = NotionIdeaManager()
    
    print(manager.add_idea("Meine neue Idee", tags=["Spike", "Feature"], status="Überlegung"))

    all_ideas = manager.get_all_ideas()
    for idea in all_ideas:
        print(f"💡 {idea['name']} (Status: {idea['status']}, Tags: {', '.join(idea['tags'])})")
