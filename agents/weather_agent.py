import python_weather
import asyncio

class WeatherClient:
    def __init__(self, city: str):
        self.city = city

    async def _fetch_weather(self):
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            weather = await client.get(self.city)
            print(f"Weather data received: {weather}")  # Debugging output
            return weather

    def get_today_weather(self):
        return asyncio.run(self._fetch_today_weather())

    async def _fetch_today_weather(self):
        weather = await self._fetch_weather()
        if not weather:
            return "No weather data available"

        return {
            'temperature': weather.temperature,
            'condition': weather.description
        }

# Example usage
if __name__ == "__main__":
    client = WeatherClient("Münster")
    today_weather = client.get_today_weather()
    print(f"Today's weather: {today_weather}")
