from googleapiclient.discovery import Resource  
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Union
import os
import sys
import pytz

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
from agents.tools.google.core.google_auth import GoogleAuth  

class GoogleCalendarClient:

    def __init__(self) -> None:
        self.service: Resource = GoogleAuth.get_service("calendar", "v3")
        self.local_tz = pytz.timezone("Europe/Berlin")  

    def get_today_events(self, max_results: int = 10) -> str:
        """Gibt die heutigen Termine aus dem Hauptkalender in einem lesbaren Format zurück."""
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

        output: List[str] = ["📅 Heutige Termine:"]
        for event in events:
            start: Optional[str] = event["start"].get("dateTime", event["start"].get("date"))
            summary: str = event.get("summary", "Kein Titel")

            # Falls nur ein Datum existiert (ganztägiges Event)
            if "dateTime" in event["start"]:
                start_dt = datetime.fromisoformat(start).astimezone(self.local_tz)  
                formatted_time = start_dt.strftime("%H:%M Uhr")  
            else:
                formatted_time = "Ganztägig"

            output.append(f"- {formatted_time}: {summary}")

        return "\n".join(output)

    def create_event(
        self, 
        start_time: Union[str, datetime],
        title: str = "Neuer Termin",
        duration_hours: float = 1.5,
        timezone_str: str = "Europe/Berlin"
    ) -> Dict:

        if isinstance(start_time, str):
            try:
                start_time = datetime.strptime(start_time, "%d.%m.%Y %H:%M")  
                start_time = self.local_tz.localize(start_time)  
                start_time = start_time.astimezone(pytz.utc)  
            except ValueError:
                raise ValueError("Ungültiges Datumsformat! Erwartet: TT.MM.JJJJ HH:MM")

        elif not isinstance(start_time, datetime):
            raise TypeError("start_time muss entweder ein datetime-Objekt oder ein String im Format 'TT.MM.JJJJ HH:MM' sein.")

        end_time = start_time + timedelta(hours=duration_hours)

        event_data = {
            "summary": title,
            "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
            "colorId": "1",  # Farbe Blau
        }

        event = self.service.events().insert(calendarId="primary", body=event_data).execute()
        return event

# Testlauf
if __name__ == "__main__":
    calendar_client = GoogleCalendarClient()
    print(calendar_client.get_today_events())
    # Beispiel mit deutscher Zeitangabe

