import python_weather
from agents.tools.weather.location_finder import LocationFinder

class WeatherClient:
    def __init__(self):
        self.city = LocationFinder.get_location()

    async def _fetch_weather(self):
        """Fetches weather data asynchronously."""
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            return await client.get(self.city)

    async def fetch_weather_data(self):
        """Fetches weather data and handles errors."""
        try:
            weather = await self._fetch_weather()
            output = [f"Wetter in {self.city}:", f"Aktuelle Temperatur: {weather.temperature}°C"]

            for daily in weather:
                output.append(str(daily))
                for hourly in daily:
                    output.append(f' --> {hourly!r}')
                    
            return output
        
        except Exception as e:
            return [f"❌ Fehler beim Abrufen der Wetterdaten: {str(e)}"]