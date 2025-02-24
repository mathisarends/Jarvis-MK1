from typing import Dict, Any
import datetime

from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_response import ToolResponse
from agents.tools.fitbit.fitbit_client_factory import FitbitClientFactory

class FitbitTool(Tool):
    def __init__(self):
        self.sleep_client, self.activity_client = FitbitClientFactory.create_clients()
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_fitbit_data",
            description="Fetch Fitbit data including sleep and activity metrics. Comparisons with previous days are only included if explicitly requested.",
            parameters={
                "include_sleep": ToolParameter(
                    type="boolean",
                    description="Include sleep data in the response. Defaults to True.",
                    required=False,
                    default=True
                ),
                "include_activity": ToolParameter(
                    type="boolean",
                    description="Include activity data in the response. Defaults to True.",
                    required=False,
                    default=True
                ),
                "compare": ToolParameter(
                    type="boolean",
                    description="Compare with the last 5 days. Defaults to False.",
                    required=False,
                    default=False
                )
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        today = datetime.date.today().strftime("%Y-%m-%d")
        include_sleep = parameters.get("include_sleep", True)
        include_activity = parameters.get("include_activity", False)
        compare = parameters.get("compare", False)

        response_parts = []

        if include_sleep:
            today_sleep = await self.sleep_client.get_daily_summary(today)
            response_parts.append(self.sleep_client.format_daily_summary(today_sleep))
            
            if compare and today_sleep:
                sleep_comparison = await self.sleep_client.get_multi_day_summary()
                if sleep_comparison:
                    response_parts.append(self.sleep_client.format_multi_day_summary(sleep_comparison))

        if include_activity:
            today_activity = await self.activity_client.fetch_data(today)
            activity_summary = self.activity_client.get_daily_summary(today_activity)
            response_parts.append(self.activity_client.format_daily_summary(activity_summary))
            
            if compare and today_activity:
                activity_comparison = await self.activity_client.get_multi_day_summary()
                if activity_comparison:
                    response_parts.append(self.activity_client.format_multi_day_summary(activity_comparison))

        if not response_parts or all(part.endswith("verfügbar.") for part in response_parts):
            return ToolResponse(
                "Es sind keine Fitbit-Daten verfügbar. Bitte stelle sicher, dass dein Fitbit synchronisiert ist.",
                "Empfehle dem Nutzer, das Fitbit zu synchronisieren und es später erneut zu versuchen."
            )

        response_text = " ".join(response_parts)
        instruction_text = """
        - Antworte in natürlicher Sprache, da die Antwort gesprochen wird.
        - Fasse die wichtigsten Trends zusammen, ohne zu viele Details zu nennen.
        - Hebe besondere Leistungen oder Verbesserungen positiv hervor.
        """

        return ToolResponse(response_text, instruction_text)