from typing import Dict, Any
from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_response import ToolResponse
from agents.tools.volume_regulation.volume_control import VolumeControl
from audio.standard_phrase_player import StandardPhrasePlayer

class VolumeControlTool(Tool):
    def __init__(self):
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="volume_control",
            description="Controls the system volume with PulseAudio (Linux).",
            parameters={
                "action": ToolParameter(
                    type="string",
                    description="The volume action to perform: 'set', 'increase', 'decrease'.",
                    required=True
                ),
                "value": ToolParameter(
                    type="integer",
                    description="The volume level (1-10) for 'set'. Not required for 'increase' or 'decrease'.",
                    required=False
                )
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        try:
            action = parameters.get("action")
            value = parameters.get("value")

            if action == "set":
                if value is None:
                    return ToolResponse("Error: 'value' is required for 'set'.", "No volume change occurred.")

                VolumeControl.set_volume_level(value)
            
            elif action == "increase":
                VolumeControl.increase_volume()
            
            elif action == "decrease":
                VolumeControl.decrease_volume()
            
            else:
                return ToolResponse(f"Error: Unknown action '{action}'", "Invalid volume action.")

            current_volume = VolumeControl.get_volume()
            StandardPhrasePlayer.play_volume_audio(current_volume)

            return ToolResponse(
                f"Volume action '{action}' executed successfully. Current volume: {current_volume}%.",
                f"Your system volume is now at {current_volume}%.",
                audio_response_handled=True
            )

        except Exception as e:
            print("Fehler ist passiert aber was?", e)
            return ToolResponse(f"Error executing VolumeControlTool: {str(e)}", "Volume change failed.")

