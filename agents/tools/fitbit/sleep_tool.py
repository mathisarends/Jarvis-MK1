from typing import Dict, Any
import datetime

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
            description="Fetch Fitbit sleep data for today. Comparison with previous days is only included if explicitly requested.",
            parameters={
                "compare": ToolParameter(
                    type="boolean",
                    description="Set to True if you want a comparison with the last 5 days. Defaults to False.",
                    required=False,
                    default=False
                )
            }
        )

    def _convert_minutes_to_hours(self, minutes: int) -> float:
        """Convert minutes to hours with one decimal precision."""
        return round(minutes / 60, 1)

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        """Fetch sleep data for today and optionally compare with past days."""
        today = datetime.date.today().strftime("%Y-%m-%d")
        compare = parameters.get("compare", False)

        today_summary = await self.fitbit_api.get_sleep_summary(today)
        if not today_summary:
            return ToolResponse(
                f"Heute sind keine Schlafdaten verfügbar. Stelle sicher, dass dein Fitbit synchronisiert ist.",
                "Falls keine Daten vorliegen, kann es helfen, Fitbit erneut zu synchronisieren."
            )

        sleep_duration = self._convert_minutes_to_hours(today_summary["sleep_duration"])
        sleep_stages = {
            stage: self._convert_minutes_to_hours(time) for stage, time in today_summary["sleep_stages"].items()
        }

        response_text = f"Du hast heute {sleep_duration} Stunden geschlafen. "
        response_text += f"Dein Schlaf bestand aus {sleep_stages['deep']} Stunden Tiefschlaf, {sleep_stages['light']} Stunden Leichtschlaf, "
        response_text += f"{sleep_stages['rem']} Stunden REM-Schlaf und {sleep_stages['wake']} Stunden Wachphasen."

        if not compare:
            return ToolResponse(response_text, """
            - Antworte kompakt und direkt.
            - Erwähne nur die Schlafdaten von heute.
            - Verwende eine natürliche Sprache, da die Antwort gesprochen wird.
            """)

        last_5_days_summary = await self.fitbit_api.get_last_5_days_sleep_summary()
        if not last_5_days_summary:
            return ToolResponse(response_text, """
            - Vergleichsdaten sind nicht verfügbar.
            - Erwähne keine Vergleiche, sondern konzentriere dich nur auf die heutigen Daten.
            """)

        avg_sleep_time = self._convert_minutes_to_hours(last_5_days_summary["average_sleep_time"])
        avg_sleep_stages = {
            stage: self._convert_minutes_to_hours(time) for stage, time in last_5_days_summary["average_sleep_stages"].items()
        }

        response_text += f" Im Vergleich zu den letzten fünf Tagen hast du im Durchschnitt {avg_sleep_time} Stunden geschlafen. "
        response_text += f"Üblicherweise hast du {avg_sleep_stages['deep']} Stunden Tiefschlaf, {avg_sleep_stages['light']} Stunden Leichtschlaf, "
        response_text += f"{avg_sleep_stages['rem']} Stunden REM-Schlaf und {avg_sleep_stages['wake']} Stunden Wachphasen."

        return ToolResponse(response_text, """
        - Vergleiche nur, wenn explizit danach gefragt wird.
        - Die Antwort sollte kompakt und natürlich klingen.
        - Erwähne nicht zu viele Details, sondern fasse die Trends zusammen.
        """)
