import logging
import aiohttp
import asyncio
import datetime
from typing import List, Optional, Dict, Any

from agents.tools.fitbit.fitbit_authenticator import FitbitAuthenticator

class FitbitDataClient:
    """Base class for Fitbit API data fetching."""
    
    BASE_URL = "https://api.fitbit.com/1.2/user/-"
    
    def __init__(self, authenticator: FitbitAuthenticator):
        self.authenticator = authenticator
        self.logger = logging.getLogger(__name__)

    async def _request_with_reauth(self, url: str) -> Optional[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.authenticator.get_auth_header()) as response:
                if response.status == 200:
                    return await response.json()
                    
                if response.status != 401:
                    self.logger.error(f"API request failed: {await response.text()}")
                    return None

                if not self.authenticator._update_access_token():
                    self.logger.error("Token refresh failed")
                    return None

                async with session.get(url, headers=self.authenticator.get_auth_header()) as retry_response:
                    if retry_response.status != 200:
                        self.logger.error(f"Retry failed: {await retry_response.text()}")
                        return None
                    return await retry_response.json()

    async def _get_multi_day_data(self, days: int, date_processor: callable) -> List[Dict[str, Any]]:
        """Generic method to fetch multiple days of data."""
        today = datetime.date.today()
        dates = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") 
                for i in range(days)]
        
        results = await asyncio.gather(*[date_processor(date) for date in dates])
        return [r for r in results if r is not None]