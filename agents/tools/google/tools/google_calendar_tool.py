from typing import Dict, Any
from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_response import ToolResponse
from agents.tools.google.clients.google_calendar_client import GoogleCalendarClient

class GoogleCalendarTool(Tool):
    """Tool zur Abfrage und Erstellung von Google Calendar Terminen."""

    def __init__(self):
        self.calendar_client = GoogleCalendarClient()
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="google_calendar_tool",
            description="Retrieves today's events from Google Calendar or creates a new event.",
            parameters={
                "action": ToolParameter(
                    type="string",
                    description="The action to perform: 'get_events' or 'create_event'.",
                    required=True
                ),
                "max_results": ToolParameter(
                    type="integer",
                    description="Number of events to retrieve (default: 10). Only used if action='get_events'.",
                    required=False
                ),
                "title": ToolParameter(
                    type="string",
                    description="Title of the new event (default: 'Neuer Termin'). Only used if action='create_event'.",
                    required=False
                ),
                "start_time": ToolParameter(
                    type="string",
                    description="Start time in 'DD.MM.YYYY HH:MM' format. Required if action='create_event'.",
                    required=False
                ),
                "duration_hours": ToolParameter(
                    type="number",
                    description="Duration in hours (default: 1.5). Only used if action='create_event'.",
                    required=False
                )
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        """
        Führt je nach 'action' eine Abfrage der heutigen Events durch
        oder erstellt einen neuen Termin im Kalender.
        """
        try:
            action = parameters.get("action")

            if action == "get_events":
                max_results = parameters.get("max_results", 10)
                events_str = self.calendar_client.get_today_events(max_results)
                return ToolResponse(events_str, "")

            elif action == "create_event":
                start_time = parameters.get("start_time")
                print("start_time", start_time)
                if not start_time:
                    return ToolResponse(
                        "Fehlender Parameter: 'start_time' ist erforderlich für 'create_event'.", 
                        ""
                    )

                title = parameters.get("title", "Neuer Termin")
                duration_hours = parameters.get("duration_hours", 1.5)

                new_event = self.calendar_client.create_event(
                    start_time=start_time,
                    title=title,
                    duration_hours=duration_hours
                )

                summary = new_event.get("summary", "(Unbekannter Titel)")
                return ToolResponse(
                    f"Neuer Termin erstellt: {summary}"
                )

            else:
                return ToolResponse(
                    "Ungültige Aktion. Bitte nutze 'get_events' oder 'create_event'.", 
                    ""
                )

        except Exception as e:
            return ToolResponse(f"Fehler beim Ausführen des Tools: {str(e)}", "")
