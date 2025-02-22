from dataclasses import dataclass

@dataclass
class ToolResponse:
    content: str
    behavior_instructions: str = ""