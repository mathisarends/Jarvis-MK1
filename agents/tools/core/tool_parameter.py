from dataclasses import dataclass

@dataclass
class ToolParameter:
    type: str
    description: str
    required: bool = False

