from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_response import ToolResponse

class Tool(ABC):
    def __init__(self):
        self.definition = self.get_definition()

    @abstractmethod
    def get_definition(self) -> ToolDefinition:
        """Return the tool's definition including name, description, and parameters"""
        pass

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        """Execute the tool's functionality with the given parameters"""
        pass

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool):
        """Register a new tool"""
        self._tools[tool.definition.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self._tools.get(name)

    def get_all_definitions(self) -> List[dict]:
        """Get all tool definitions in OpenAI format"""
        return [tool.definition.to_openai_schema() for tool in self._tools.values()]