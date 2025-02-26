from googleapiclient.discovery import Resource  
from datetime import datetime, timezone
from typing import List, Dict, Optional
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
from agents.tools.google.core.google_auth import GoogleAuth  

class GoogleCalendarClient:

    def __init__(self) -> None:
        self.service: Resource = GoogleAuth.get_service("calendar", "v3")

    def get_today_events(self, max_results: int = 10) -> str:
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()

        events_result: Dict = self.service.events().list(
            calendarId="primary",  
            timeMin=start_of_day,
            timeMax=end_of_day,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events: List[Dict] = events_result.get("items", [])

        if not events:
            return "📅 Heute gibt es keine Termine."

        output: List[str] = ["📅 **Deine heutigen Termine:**"]
        for event in events:
            start: Optional[str] = event["start"].get("dateTime", event["start"].get("date"))
            summary: str = event.get("summary", "Kein Titel")
            output.append(f"- {start}: {summary}")

        return "\n".join(output)

if __name__ == "__main__":
    calendar_client = GoogleCalendarClient()
    print(calendar_client.get_today_events())
