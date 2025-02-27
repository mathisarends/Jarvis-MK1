from agents.tools.notion.core.notion_config import NOTION_PAGES, NOTION_DATABASES

class NotionPages:
    """Centralized access to Notion pages and databases."""
    
    @staticmethod
    def get_page_id(name: str) -> str:
        return NOTION_PAGES.get(name.upper(), "UNKNOWN_PAGE")

    @staticmethod
    def get_database_id(name: str) -> str:
        return NOTION_DATABASES.get(name.upper(), "UNKNOWN_DATABASE")

    @staticmethod
    def list_all():
        """Returns a formatted list of all pages and databases."""
        output = ["📄 Important Pages:"]
        output += [f"- {name}: {id}" for name, id in NOTION_PAGES.items()]
        output.append("\n🗂 Important Databases:")
        output += [f"- {name}: {id}" for name, id in NOTION_DATABASES.items()]
        return "\n".join(output)