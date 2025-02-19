import os
from typing import Optional
import python_weather
import asyncio
from location_finder import LocationFinder

class WeatherClient:
    def __init__(self, city: Optional[str] = None):
        if city is not None:
            self.city = city
        else: 
            self.city = LocationFinder.get_location()

    async def _fetch_weather(self):
        """Fetches weather data asynchronously."""
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            return await client.get(self.city)

    def get_weather(self):
        """Runs the async function to fetch weather data and returns the output as a list of strings."""
        return asyncio.run(self._fetch_weather_data())

    async def _fetch_weather_data(self):
        """Fetches weather data and formats it as a list of strings."""
        weather = await self._fetch_weather()

        output = []
        
        output.append(f"Aktuelle Temperatur: {weather.temperature}°C")

        for daily in weather:
            output.append(str(daily))  
            
            for hourly in daily:
                output.append(f' --> {hourly!r}')  

        return output