import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
import concurrent.futures
from agents.tools.notion.core.abstract_notion_client import AbstractNotionClient
from agents.tools.notion.core.notion_pages import NotionPages


class NotionTodoManager(AbstractNotionClient):
    def __init__(self):
        super().__init__()
        self.database_id = NotionPages.get_database_id("TODOS")  

    def add_todo(self, title, priority="Mittel", status="Nicht begonnen", done=False):
        """Adds a new TODO to the database with priority and status."""
        
        data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Titel": {
                    "title": [{"text": {"content": title}}]
                },
                "Priorität": {
                    "select": {"name": priority}
                },
                "Status": {
                    "status": {"name": status}
                },
                "Fertig": {
                    "checkbox": done
                }
            }
        }

        try:
            response = self._make_request("post", "pages", data)

            if response.status_code == 200:
                self.logger.info(f"✅ TODO added: {title}")
                return f"✅ TODO '{title}' added successfully."
            else:
                self.logger.error(f"❌ Error adding TODO: {response.text}")
                return f"❌ Error adding TODO: {response.text}"

        except Exception as e:
            self.logger.error(f"❌ API call failed: {str(e)}")
            return f"❌ API call failed: {str(e)}"

    def get_all_todos(self):
        """Retrieves only open TODOs (Fertig = False) and sorts them by priority."""
        raw_todos = self._get_raw_todos()
        return self._format_todo_list(raw_todos)

    def get_daily_top_tasks(self):
        """Retrieves only TODOs with the priority 'Daily Top Task'."""
        try:
            raw_todos = self._get_raw_todos()  # Holt die unbearbeitete Liste
            daily_top_tasks = [todo for todo in raw_todos if todo["priority"] == "Daily Top Task"]

            return self._format_todo_list(daily_top_tasks)

        except Exception as e:
            self.logger.error(f"❌ API call failed: {str(e)}")
            return f"API call failed: {str(e)}"
        
    def _get_raw_todos(self):
        """Helper function to retrieve raw TODOs as a list."""
        try:
            response = self._make_request("post", f"databases/{self.database_id}/query")

            if response.status_code != 200:
                self.logger.error(f"❌ Error retrieving TODOs: {response.text}")
                return []

            results = response.json().get("results", [])
            
            priority_order = {
                "Daily Top Task": 1,
                "Hoch": 2,
                "Mittel": 3,
                "Niedrig": 4
            }

            open_todos = [
                {
                    "id": item["id"],
                    "title": item["properties"]["Titel"]["title"][0]["text"]["content"],
                    "priority": item["properties"]["Priorität"]["select"]["name"],
                    "status": item["properties"]["Status"]["status"]["name"],
                    "done": item["properties"]["Fertig"]["checkbox"]
                }
                for item in results if not item["properties"]["Fertig"]["checkbox"]
            ]

            open_todos.sort(key=lambda todo: priority_order.get(todo["priority"], 99))
            return open_todos

        except Exception as e:
            self.logger.error(f"❌ API call failed: {str(e)}")
            return []


    def _format_todo_list(self, todos):
        """Formats the TODO list into a readable string without icons."""
        if not todos:
            return "Keine offenen TODOs vorhanden."

        formatted_todos = [f"{todo['title']} (Priorität: {todo['priority']}, Status: {todo['status']})"
                           for todo in todos]
        
        return "\n".join(formatted_todos)
        
        
if __name__ == "__main__":
    manager = NotionTodoManager()

    print("📌 **Alle offenen TODOs:**")
    print(manager.get_all_todos())

    print("\n🔥 **Daily Top Tasks:**")
    print(manager.get_daily_top_tasks())