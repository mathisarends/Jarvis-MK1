import datetime
import json
import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from agents.tools.fitbit.fitbit_client_factory import FitbitClientFactory

async def main():
    sleep_client, activity_client = FitbitClientFactory.create_clients()
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Fetch sleep data
    today_sleep = await sleep_client.get_daily_summary(today)
    sleep_summary = await sleep_client.get_multi_day_summary()
    
    print(json.dumps({
        "today_sleep": today_sleep,
        "sleep_summary": sleep_summary
    }, indent=2))
    
    print("="*80)
    
    # Fetch activity data
    today_activity = await activity_client.fetch_data(today)
    activity_summary = await activity_client.get_multi_day_summary()
    
    print(json.dumps({
        "today_activity": activity_client.get_daily_summary(today_activity),
        "activity_summary": activity_summary
    }, indent=2))

if __name__ == "__main__":
    asyncio.run(main())