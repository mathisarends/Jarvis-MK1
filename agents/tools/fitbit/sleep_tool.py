from typing import Dict, Any
from datetime import date

from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_response import ToolResponse
from agents.tools.fitbit.fitbit_client import FitbitClient

class SleepTool(Tool):
    def __init__(self):
        self.fitbit_api = FitbitClient()
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_sleep_data",
            description="Get Fitbit sleep data summary for a specific date.",
            parameters={
                "date": ToolParameter(
                    type="string",
                    description="The date to fetch sleep data for (YYYY-MM-DD). Defaults to today if not provided.",
                    required=False
                )
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        sleep_behavior = """
        When presenting sleep data:
        1. Start with a clear summary of total sleep time and time in bed.
        2. Provide sleep stage details if available (e.g., Deep, Light, REM, Awake).
        3. If sleep efficiency seems low, suggest possible improvements.
        4. Use phrases like "You slept a total of..." or "Your sleep breakdown is as follows..."
        5. If no data is available, acknowledge it and suggest checking Fitbit synchronization.
        """

        try:
            target_date = parameters.get("date", date.today().isoformat())
            sleep_data = self.fitbit_api.get_sleep_data(target_date)

            if not sleep_data:
                return ToolResponse(
                    f"No sleep data available for {target_date}",
                    sleep_behavior
                )

            summary = [
                f"Sleep Summary for {target_date}:",
                f"Total Sleep Time: {sleep_data.get('totalMinutesAsleep', 0)} minutes",
                f"Total Time in Bed: {sleep_data.get('totalTimeInBed', 0)} minutes"
            ]

            stages = sleep_data.get('stages', {})
            if stages:
                summary.append("\nSleep Stages:")
                for stage, minutes in stages.items():
                    summary.append(f"- {stage}: {minutes} minutes")

            return ToolResponse("\n".join(summary), sleep_behavior)

        except Exception as e:
            return ToolResponse(f"Error fetching sleep data: {str(e)}", sleep_behavior)
