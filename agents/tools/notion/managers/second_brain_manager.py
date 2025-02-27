from agents.tools.notion.core.notion_pages import NotionPages

class SecondBrainManager:
    def __init__(self):
        super().__init__()
        self.database_id = NotionPages.get_database_id("WISSEN_NOTIZEN")