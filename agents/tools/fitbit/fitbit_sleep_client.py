from typing import Any, Dict, Optional
from agents.tools.fitbit.fitbit_data_client import FitbitDataClient

class FitbitSleepClient(FitbitDataClient):

    def _convert_minutes_to_hours(self, minutes: int) -> float:
        return round(minutes / 60, 1)

    async def fetch_data(self, date: str) -> Optional[Dict[str, Any]]:
        url = f"{self.BASE_URL}/sleep/date/{date}.json"
        return await self._request_with_reauth(url)

    def _get_sleep_stages(self, sleep_entry: Dict[str, Any]) -> Dict[str, int]:
        stages = sleep_entry.get("levels", {}).get("summary", {})
        return {
            "deep": stages.get("deep", {}).get("minutes", 0),
            "light": stages.get("light", {}).get("minutes", 0),
            "rem": stages.get("rem", {}).get("minutes", 0),
            "wake": stages.get("wake", {}).get("minutes", 0)
        }

    async def get_daily_summary(self, date: str) -> Optional[Dict[str, Any]]:
        sleep_data = await self.fetch_data(date)
        
        if not sleep_data or "sleep" not in sleep_data or not sleep_data["sleep"]:
            return None
            
        main_sleep = sleep_data["sleep"][0]
        return {
            "date": date,
            "start_time": main_sleep.get("startTime"),
            "end_time": main_sleep.get("endTime"),
            "sleep_duration": main_sleep.get("minutesAsleep", 0),
            "sleep_stages": self._get_sleep_stages(main_sleep)
        }

    def format_daily_summary(self, sleep_summary: Optional[Dict[str, Any]]) -> str:
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

    async def get_multi_day_summary(self, days: int = 6) -> Dict[str, Any]:
        sleep_summaries = await self._get_multi_day_data(days, self.get_daily_summary)
        
        if not sleep_summaries:
            return {
                "total_sleep_time": 0,
                "average_sleep_time": 0,
                "average_sleep_stages": {"deep": 0, "light": 0, "rem": 0, "wake": 0},
                "sleep_sessions": []
            }

        total_sleep_time = sum(s["sleep_duration"] for s in sleep_summaries)
        
        return {
            "total_sleep_time": total_sleep_time,
            "average_sleep_time": total_sleep_time // len(sleep_summaries),
            "average_sleep_stages": {
                stage: sum(s["sleep_stages"][stage] for s in sleep_summaries) // len(sleep_summaries)
                for stage in ["deep", "light", "rem", "wake"]
            },
            "sleep_sessions": sleep_summaries
        }

    def format_multi_day_summary(self, summary: Dict[str, Any]) -> str:
        avg_sleep_time = self._convert_minutes_to_hours(summary["average_sleep_time"])
        avg_stages = {
            stage: self._convert_minutes_to_hours(time) 
            for stage, time in summary["average_sleep_stages"].items()
        }

        return (
            f"Im Vergleich zu den letzten fünf Tagen hast du im Durchschnitt "
            f"{avg_sleep_time} Stunden geschlafen. Üblicherweise hast du "
            f"{avg_stages['deep']} Stunden Tiefschlaf, "
            f"{avg_stages['light']} Stunden Leichtschlaf, "
            f"{avg_stages['rem']} Stunden REM-Schlaf und "
            f"{avg_stages['wake']} Stunden Wachphasen."
        )
