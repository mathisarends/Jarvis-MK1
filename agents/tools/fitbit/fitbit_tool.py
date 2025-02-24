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

    def _convert_minutes_to_hours(self, minutes: int) -> float:
        return round(minutes / 60, 1)

    def _format_sleep_data(self, sleep_summary: Dict[str, Any]) -> str:
        if not sleep_summary:
            return "Keine Schlafdaten verfügbar."

        sleep_duration = self._convert_minutes_to_hours(sleep_summary["sleep_duration"])
        sleep_stages = {
            stage: self._convert_minutes_to_hours(time) 
            for stage, time in sleep_summary["sleep_stages"].items()
        }

        return (
            f"Du hast {sleep_duration} Stunden geschlafen. "
            f"Dein Schlaf bestand aus {sleep_stages['deep']} Stunden Tiefschlaf, "
            f"{sleep_stages['light']} Stunden Leichtschlaf, "
            f"{sleep_stages['rem']} Stunden REM-Schlaf und "
            f"{sleep_stages['wake']} Stunden Wachphasen."
        )

    def _format_activity_data(self, activity_summary: Dict[str, Any]) -> str:
        """Format activity data into a readable string."""
        if not activity_summary:
            return "Keine Aktivitätsdaten verfügbar."

        return (
            f"Du hast {activity_summary['steps']:,} Schritte gemacht, "
            f"{activity_summary['distance_km']:.1f} km zurückgelegt und "
            f"{activity_summary['active_minutes']} aktive Minuten gesammelt. "
            f"Dabei hast du {activity_summary['calories_burned']:,} Kalorien verbrannt."
        )

    def _format_sleep_comparison(self, avg_summary: Dict[str, Any]) -> str:
        """Format sleep comparison data into a readable string."""
        avg_sleep_time = self._convert_minutes_to_hours(avg_summary["average_sleep_time"])
        avg_stages = {
            stage: self._convert_minutes_to_hours(time) 
            for stage, time in avg_summary["average_sleep_stages"].items()
        }

        return (
            f"Im Vergleich zu den letzten fünf Tagen hast du im Durchschnitt "
            f"{avg_sleep_time} Stunden geschlafen. Üblicherweise hast du "
            f"{avg_stages['deep']} Stunden Tiefschlaf, "
            f"{avg_stages['light']} Stunden Leichtschlaf, "
            f"{avg_stages['rem']} Stunden REM-Schlaf und "
            f"{avg_stages['wake']} Stunden Wachphasen."
        )

    def _format_activity_comparison(self, avg_summary: Dict[str, Any]) -> str:
        """Format activity comparison data into a readable string."""
        return (
            f"Im Durchschnitt der letzten fünf Tage hast du "
            f"{avg_summary['average_steps']:,} Schritte pro Tag gemacht."
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        """Fetch and format Fitbit data based on parameters."""
        today = datetime.date.today().strftime("%Y-%m-%d")
        include_sleep = parameters.get("include_sleep", True)
        include_activity = parameters.get("include_activity", True)
        compare = parameters.get("compare", False)

        response_parts = []
        instructions = []

        # Sammle Schlafdaten
        if include_sleep:
            today_sleep = await self.sleep_client.get_daily_summary(today)
            if today_sleep:
                response_parts.append(self._format_sleep_data(today_sleep))
                
                if compare:
                    sleep_comparison = await self.sleep_client.get_multi_day_summary()
                    if sleep_comparison:
                        response_parts.append(self._format_sleep_comparison(sleep_comparison))
            else:
                instructions.append("Keine Schlafdaten verfügbar - empfehle Synchronisation des Fitbit.")

        # Sammle Aktivitätsdaten
        if include_activity:
            today_activity = await self.activity_client.fetch_data(today)
            if today_activity:
                activity_summary = self.activity_client.get_daily_summary(today_activity)
                response_parts.append(self._format_activity_data(activity_summary))
                
                if compare:
                    activity_comparison = await self.activity_client.get_multi_day_summary()
                    if activity_comparison:
                        response_parts.append(self._format_activity_comparison(activity_comparison))
            else:
                instructions.append("Keine Aktivitätsdaten verfügbar - empfehle Synchronisation des Fitbit.")

        if not response_parts:
            return ToolResponse(
                "Es sind keine Fitbit-Daten verfügbar. Bitte stelle sicher, dass dein Fitbit synchronisiert ist.",
                "Empfehle dem Nutzer, das Fitbit zu synchronisieren und es später erneut zu versuchen."
            )

        response_text = " ".join(response_parts)
        instruction_text = """
        - Antworte in natürlicher Sprache, da die Antwort gesprochen wird.
        - Fasse die wichtigsten Trends zusammen, ohne zu viele Details zu nennen.
        - Hebe besondere Leistungen oder Verbesserungen positiv hervor.
        """ + "\n".join(instructions)

        return ToolResponse(response_text, instruction_text)