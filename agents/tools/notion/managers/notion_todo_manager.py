import sys
import os
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
from agents.tools.notion.core.abstract_notion_client import AbstractNotionClient
from agents.tools.notion.core.notion_pages import NotionPages


class NotionTodoManager(AbstractNotionClient):
    def __init__(self):
        super().__init__()
        self.database_id = NotionPages.get_database_id("TODOS")  

    async def add_todo(self, title, priority="Mittel", status="Nicht begonnen", done=False):
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
            response = await self._make_request("post", "pages", data)

            if response.status_code == 200:
                self.logger.info(f"✅ TODO added: {title}")
                return f"✅ TODO '{title}' added successfully."
            else:
                self.logger.error(f"❌ Error adding TODO: {response.text}")
                return f"❌ Error adding TODO: {response.text}"

        except Exception as e:
            self.logger.error(f"❌ API call failed: {str(e)}")
            return f"❌ API call failed: {str(e)}"

    async def get_all_todos(self):
        """Retrieves only open TODOs (Fertig = False) and sorts them by priority."""
        raw_todos = await self._get_raw_todos()
        return self._format_todo_list(raw_todos)

    async def get_daily_top_tasks(self):
        """Retrieves only TODOs with the priority 'Daily Top Task'."""
        try:
            raw_todos = await self._get_raw_todos()  # Holt die unbearbeitete Liste
            daily_top_tasks = [todo for todo in raw_todos if todo["priority"] == "Daily Top Task"]

            return self._format_todo_list(daily_top_tasks)

        except Exception as e:
            self.logger.error(f"❌ API call failed: {str(e)}")
            return f"API call failed: {str(e)}"
        
    async def _get_raw_todos(self):
        try:
            results = await self._fetch_todos_from_notion()
            if not results:
                return []
            
            open_todos = self._process_todo_results(results)
            
            sorted_todos = self._sort_todos_by_priority(open_todos)
            
            return sorted_todos
            
        except Exception as e:
            self.logger.error(f"❌ API call failed: {str(e)}")
            return []

    async def _fetch_todos_from_notion(self):
        response = await self._make_request("post", f"databases/{self.database_id}/query")
        
        return response.json().get("results", [])

    def _process_todo_results(self, results):
        open_todos = []
        
        for item in results:
            if item.get("properties", {}).get("Fertig", {}).get("checkbox", True):
                continue
            
            try:
                todo_item = self._extract_todo_data(item)
                if todo_item:
                    open_todos.append(todo_item)
            except Exception as e:
                self.logger.error(f"❌ Error processing TODO item: {str(e)}")
                continue
        
        return open_todos

    def _extract_todo_data(self, item):
        title_content = item.get("properties", {}).get("Titel", {}).get("title", [])
        title = "Untitled Task"
        
        if title_content and len(title_content) > 0:
            title = title_content[0].get("text", {}).get("content", "Untitled Task")
        
        priority = item.get("properties", {}).get("Priorität", {}).get("select", {})
        priority_name = priority.get("name", "Mittel") if priority else "Mittel"
        
        status = item.get("properties", {}).get("Status", {}).get("status", {})
        status_name = status.get("name", "Nicht begonnen") if status else "Nicht begonnen"
        
        return {
            "id": item.get("id", ""),
            "title": title,
            "priority": priority_name,
            "status": status_name,
            "done": False
        }

    def _sort_todos_by_priority(self, todos):
        """Sort todos by priority."""
        priority_order = {
            "Daily Top Task": 1,
            "Hoch": 2,
            "Mittel": 3,
            "Niedrig": 4
        }
        
        return sorted(todos, key=lambda todo: priority_order.get(todo["priority"], 99))


    def _format_todo_list(self, todos):
        """Formats the TODO list into a readable string without icons."""
        if not todos:
            return "Keine offenen TODOs vorhanden."

        formatted_todos = [f"{i + 1}. {todo['title']} (Priorität: {todo['priority']}, Status: {todo['status']})"
                            for i, todo in enumerate(todos)]
            
        return "\n".join(formatted_todos)
        
        
async def main():
    manager = NotionTodoManager()

    print("📌 **Alle offenen TODOs:**")
    print(await manager.get_all_todos())

    print("\n🔥 **Daily Top Tasks:**")
    print(await manager.get_daily_top_tasks())

if __name__ == "__main__":
    asyncio.run(main())  