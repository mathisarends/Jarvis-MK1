from dataclasses import dataclass

@dataclass
class ToolResponse:
    content: str
    behavior_instructions: str = "",
    standard_response_audio_sub_path: str = ""
    audio_response_handled: bool = False