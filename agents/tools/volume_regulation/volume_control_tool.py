from typing import Dict, Any
from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_response import ToolResponse
from agents.tools.volume_regulation.volume_control import VolumeControl

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
                    return "Error: 'value' is required for 'set'."
                VolumeControl.set_volume_level(value)
                return ToolResponse(
                    f"Volume set to {value * 10}%",
                    f"Your system volume is now set to level {value}.",
                )

            elif action == "increase":
                VolumeControl.increase_volume()
                return ToolResponse(
                    "Volume increased by 15%",
                    "Your system volume has been increased.",
                )

            elif action == "decrease":
                VolumeControl.decrease_volume()
                return ToolResponse(
                    "Volume decreased by 15%",
                    "Your system volume has been decreased.",
                )

            else:
                return f"Error: Unknown action '{action}'"

        except Exception as e:
            return f"Error executing VolumeControlTool: {str(e)}"
