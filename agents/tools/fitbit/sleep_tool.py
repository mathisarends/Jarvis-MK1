from typing import Dict, Any
from datetime import date

from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_parameter import ToolParameter
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

    async def execute(self, parameters: Dict[str, Any]) -> str:
        try:
            target_date = parameters.get("date", date.today().isoformat())
            
            sleep_data = self.fitbit_api.get_sleep_data(target_date)
            
            if not sleep_data:
                return f"No sleep data available for {target_date}"

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

            return "\n".join(summary)
        except Exception as e:
            return f"Error fetching sleep data: {str(e)}"