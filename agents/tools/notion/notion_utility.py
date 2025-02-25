from agents.tools.notion.core.abstract_notion_client import AbstractNotionClient

class NotionUtility(AbstractNotionClient):
    """Utility class for general Notion operations."""
    
    def get_accessible_pages(self):
        """Retrieves all Notion pages accessible with the current API token."""
        response = self._make_request(
            "post", 
            "search", 
            {"filter": {"value": "page", "property": "object"}}
        )

        if response.status_code != 200:
            self.logger.error(f"Error retrieving pages: {response.text}")
            return f"Error retrieving pages: {response.text}"

        pages = response.json().get("results", [])
        if not pages:
            return "No accessible pages found."

        formatted_pages = []
        for page in pages:
            page_id = page["id"]
            title = self._extract_page_title(page)
            formatted_pages.append(f"- {title} (ID: {page_id})")

        return "\nAccessible Pages:\n" + "\n".join(formatted_pages)
    
    def get_page_children(self, page_id):
        response = self._make_request("get", f"blocks/{page_id}/children")

        if response.status_code != 200:
            self.logger.error(f"Error retrieving blocks: {response.text}")
            return f"Error retrieving blocks: {response.text}"

        return response.json()
    
    def get_database_schema(self, database_id):
        response = self._make_request("get", f"databases/{database_id}")

        if response.status_code != 200:
            self.logger.error(f"Error retrieving database: {response.text}")
            return f"Error retrieving database: {response.text}"

        return response.json()
    
    def _extract_page_title(self, page):
        if "properties" in page and "title" in page.get("properties", {}):
            title_property = page.get("properties", {}).get("title", {}).get("title", [])
            if title_property:
                return title_property[0]["text"]["content"]
                
        if "title" in page:
            title_array = page.get("title", [])
            if title_array:
                return title_array[0]["text"]["content"]
                
        return "Unnamed Page"
