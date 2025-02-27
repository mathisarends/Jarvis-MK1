import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from agents.tools.notion.core.notion_pages import NotionPages
from agents.tools.notion.managers.notion_todo_manager import NotionTodoManager
from agents.tools.notion.managers.notion_clipboard_manager import NotionClipboardManager
from agents.tools.notion.managers.notion_idea_manager import NotionIdeaManager
from agents.tools.notion.managers.notion_utility import NotionUtility

if __name__ == "__main__":
    utility = NotionUtility()
    todo_manager = NotionTodoManager()
    clipboard_manager = NotionClipboardManager()
    idea_manager = NotionIdeaManager()
    
#     markdown_text = """
# # Überschrift 1
# ## Überschrift 2
# **Fett**
# *Kursiv*
# - Liste
# - Noch ein Punkt
# > Ein Zitat
# `Inline-Code`
# """
    
    
#     # clipboard_manager.append_to_clipboard(markdown_text)      
#     result = todo_manager.get_entries_and_delete_completed()    
#     print(result)
    
        
        # Alle wichtigen Seiten & Datenbanken ausgeben
    print(NotionPages.list_all())