import re
from typing import List, Dict, Any

class NotionMarkdownParser:
    @staticmethod
    def parse_markdown(text: str) -> List[Dict[str, Any]]:
        return NotionMarkdownParser._parse_blocks(text)
    
    @staticmethod
    def _parse_blocks(text: str) -> List[Dict[str, Any]]:
        blocks = []
        lines = text.split('\n')
        
        for line in lines:
            if not line.strip():
                continue
                
            # Process headers
            header_match = re.match(r'^(#{1,6})\s(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                content = header_match.group(2)
                blocks.append({
                    "type": "heading_" + str(level),
                    f"heading_{level}": {
                        "rich_text": NotionMarkdownParser._parse_inline_formatting(content)
                    }
                })
                continue
                
            # Process lists
            list_match = re.match(r'^(\s*)[*\-+]\s(.+)$', line)
            if list_match:
                content = list_match.group(2)
                blocks.append({
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": NotionMarkdownParser._parse_inline_formatting(content)
                    }
                })
                continue
                
            # Process numbered lists
            numbered_list_match = re.match(r'^\s*\d+\.\s(.+)$', line)
            if numbered_list_match:
                content = numbered_list_match.group(1)
                blocks.append({
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": NotionMarkdownParser._parse_inline_formatting(content)
                    }
                })
                continue
                
            # Default to paragraph
            blocks.append({
                "type": "paragraph",
                "paragraph": {
                    "rich_text": NotionMarkdownParser._parse_inline_formatting(line)
                }
            })
        
        return blocks

    @staticmethod
    def _parse_inline_formatting(text: str) -> List[Dict[str, Any]]:
        """
        Verarbeitet Inline-Formatierungen im Text.
        """
        elements = []
        last_index = 0
        
        patterns = [
            (r'\*\*(.+?)\*\*', {'bold': True}),
            (r'\*(.+?)\*', {'italic': True}),
            (r'_(.+?)_', {'italic': True}),
            (r'__(.+?)__', {'underline': True}),
            (r'~~(.+?)~~', {'strikethrough': True}),
            (r'`(.+?)`', {'code': True}),
            (r'\[(.+?)\]\((.+?)\)', {'link': True}),
        ]
        
        while last_index < len(text):
            earliest_match = None
            earliest_pattern = None
            earliest_start = len(text)
            
            for pattern, formatting in patterns:
                match = re.search(pattern, text[last_index:])
                if match and (last_index + match.start()) < earliest_start:
                    earliest_match = match
                    earliest_pattern = formatting
                    earliest_start = last_index + match.start()
            
            if earliest_match and earliest_pattern:
                if earliest_start > last_index:
                    elements.append({
                        "type": "text",
                        "text": {"content": text[last_index:earliest_start]},
                        "annotations": NotionMarkdownParser._default_annotations()
                    })
                
                if 'link' in earliest_pattern:
                    elements.append({
                        "type": "text",
                        "text": {
                            "content": earliest_match.group(1),
                            "link": {"url": earliest_match.group(2)}
                        },
                        "annotations": NotionMarkdownParser._default_annotations()
                    })
                else:
                    annotations = NotionMarkdownParser._default_annotations()
                    annotations.update(earliest_pattern)
                    elements.append({
                        "type": "text",
                        "text": {"content": earliest_match.group(1)},
                        "annotations": annotations
                    })
                
                last_index = earliest_start + len(earliest_match.group(0))
            else:
                if last_index < len(text):
                    elements.append({
                        "type": "text",
                        "text": {"content": text[last_index:]},
                        "annotations": NotionMarkdownParser._default_annotations()
                    })
                break
        
        return elements

    @staticmethod
    def _default_annotations() -> Dict[str, bool]:
        """
        Erstellt Standard-Annotations-Objekt.
        """
        return {
            "bold": False,
            "italic": False,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": "default"
        }