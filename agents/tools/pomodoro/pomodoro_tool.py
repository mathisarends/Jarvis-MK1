from typing import Any, Dict
from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_response import ToolResponse
from agents.tools.pomodoro.commands.start_pomodoro_command import StartPomodoroCommand, StatusPomodoroCommand, StopPomodoroCommand

class PomodoroTool(Tool):
    def __init__(self):
        self.pomodoro_timer = None
        super().__init__()
        
        self.commands = {
            "start": StartPomodoroCommand(),
            "stop": StopPomodoroCommand(),
            "status": StatusPomodoroCommand()
        }


    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="pomodoro_tool",
            description="Manages a Pomodoro timer, allowing start, stop, and checking remaining time.",
            parameters={
                "action": ToolParameter(
                    type="string",
                    description="Action to perform: 'start', 'stop', or 'status'.",
                    required=True
                ),
                "duration_minutes": ToolParameter(
                    type="integer",
                    description="Duration of the Pomodoro timer in minutes (only required for 'start').",
                    required=False
                )
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        action = parameters.get("action")
        
        command = self.commands.get(action, None)
        
        if command is None:
            return ToolResponse("Invalid action. Use 'start', 'stop', or 'status'.")

        result_message = command.execute(self, **parameters)
        return ToolResponse(result_message)