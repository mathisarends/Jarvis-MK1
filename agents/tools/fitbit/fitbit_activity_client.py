from typing import Any, Dict, Optional
from agents.tools.fitbit.fitbit_data_client import FitbitDataClient

class FitbitActivityClient(FitbitDataClient):
    """Client for handling Fitbit activity data."""

    async def fetch_data(self, date: str) -> Optional[Dict[str, Any]]:
        url = f"{self.BASE_URL}/activities/date/{date}.json"
        return await self._request_with_reauth(url)

    def get_daily_summary(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        if not activity_data:
            return {
                "steps": 0,
                "distance_km": 0,
                "calories_burned": 0,
                "active_minutes": 0
            }
            
        summary = activity_data.get("summary", {})
        return {
            "steps": summary.get("steps", 0),
            "distance_km": next((x["distance"] for x in summary.get("distances", []) 
                               if x["activity"] == "total"), 0),
            "calories_burned": summary.get("caloriesOut", 0),
            "active_minutes": (summary.get("fairlyActiveMinutes", 0) + 
                             summary.get("veryActiveMinutes", 0))
        }

    async def get_multi_day_summary(self, days: int = 6) -> Dict[str, Any]:
        async def get_processed_daily_data(date: str) -> Optional[Dict[str, Any]]:
            data = await self.fetch_data(date)
            return self.get_daily_summary(data) if data else None

        activity_summaries = await self._get_multi_day_data(days, get_processed_daily_data)
        
        if not activity_summaries:
            return {
                "total_steps": 0,
                "average_steps": 0,
                "activity_sessions": []
            }

        total_steps = sum(s["steps"] for s in activity_summaries)
        
        return {
            "total_steps": total_steps,
            "average_steps": total_steps // len(activity_summaries),
            "activity_sessions": activity_summaries
        }