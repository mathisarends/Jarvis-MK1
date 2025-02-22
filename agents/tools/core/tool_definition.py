
from typing import Dict, Optional
from agents.tools.core.tool_parameter import ToolParameter

class ToolDefinition:
    def __init__(self, name: str, description: str, parameters: Optional[Dict[str, ToolParameter]] = None):
        self.name = name
        self.description = description
        self.parameters = parameters or {}

    def to_openai_schema(self) -> dict:
        """Convert the tool definition to OpenAI's function calling format"""
        properties = {}
        required = []
        
        for param_name, param in self.parameters.items():
            properties[param_name] = {
                "type": param.type,
                "description": param.description
            }
            if param.required:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False
                }
            }
        }