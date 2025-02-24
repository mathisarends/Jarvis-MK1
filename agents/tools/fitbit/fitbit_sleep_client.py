from typing import Any, Dict, Optional
from agents.tools.fitbit.fitbit_data_client import FitbitDataClient

class FitbitSleepClient(FitbitDataClient):
    """Client for handling Fitbit sleep data."""

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