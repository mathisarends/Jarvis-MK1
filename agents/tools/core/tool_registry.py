from typing import Dict, Optional, List
from agents.tools.core.tool import Tool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        
    def register_tools_from_module(self, module):
        for cls in module.__dict__.values():
            if isinstance(cls, type) and issubclass(cls, Tool) and cls is not Tool:
                self.register_tool(cls())

    def register_tool(self, tool: Tool):
        """Register a new tool"""
        self._tools[tool.definition.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self._tools.get(name)

    def get_all_definitions(self) -> List[dict]:
        """Get all tool definitions in OpenAI format"""
        return [tool.definition.to_openai_schema() for tool in self._tools.values()]
    
