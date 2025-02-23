from typing import Any, Dict
from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_response import ToolResponse
from agents.tools.pomodoro.pomodoro_timer import PomodoroTimer


class PomodoroTool(Tool):
    def __init__(self):
        self.pomodoro_timer = None
        super().__init__()

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
        response_message = "Invalid action. Use 'start', 'stop', or 'status'."

        if action == "start":
            duration_minutes = parameters.get("duration_minutes")
            if not duration_minutes:
                response_message = "Error: 'duration_minutes' is required for starting a timer."
            elif self.pomodoro_timer and self.pomodoro_timer.running:
                response_message = "A Pomodoro timer is already running. Stop it before starting a new one."
            else:
                self.pomodoro_timer = PomodoroTimer(duration_minutes)
                self.pomodoro_timer.start()
                response_message = f"Pomodoro timer started for {duration_minutes} minutes."
        
        elif action == "stop":
            if not self.pomodoro_timer or not self.pomodoro_timer.running:
                response_message = "No active Pomodoro timer to stop."
            else:
                self.pomodoro_timer.stop()
                response_message = "Pomodoro timer stopped."
        
        elif action == "status":
            if not self.pomodoro_timer or not self.pomodoro_timer.running:
                response_message = "No active Pomodoro timer."
            else:
                response_message = self.pomodoro_timer.get_remaining_time()
        
        return ToolResponse(response_message)