from agents.tools.notion.core.abstract_notion_client import AbstractNotionClient
from agents.tools.notion.notion_markdown_parser import NotionMarkdownParser


class NotionClipboardManager(AbstractNotionClient):
    """Class for managing clipboard content in Notion."""
    
    def __init__(self, clipboard_page_id="1a3389d5-7bd3-80d7-a507-e67d1b25822c"):
        super().__init__()
        self.clipboard_page_id = clipboard_page_id
    
    def append_to_clipboard(self, text):
        """Appends formatted text to the clipboard page with a divider."""
        divider_block = {
            "type": "divider",
            "divider": {}
        }
        
        content_blocks = NotionMarkdownParser.parse_markdown(text)
        
        data = {
            "children": [divider_block] + content_blocks
        }
        
        response = self._make_request(
            "patch", 
            f"blocks/{self.clipboard_page_id}/children", 
            data
        )
        
        if response.status_code == 200:
            self.logger.info("Text successfully added to clipboard page.")
            return "Text successfully added to clipboard page."
        else:
            self.logger.error(f"Error adding text: {response.text}")
            return f"Error adding text: {response.text}"