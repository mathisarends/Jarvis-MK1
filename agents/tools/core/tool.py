from typing import Dict, Any
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