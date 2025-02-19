import python_weather
import asyncio
import os

class WeatherClient:
    def __init__(self, city: str):
        self.city = city

    async def _fetch_weather(self):
        """Fetches weather data asynchronously."""
        async with python_weather.Client(unit=python_weather.METRIC) as client:  # Celsius statt Fahrenheit
            return await client.get(self.city)

    def get_weather(self):
        """Runs the async function to fetch weather data."""
        return asyncio.run(self._fetch_weather_data())

    async def _fetch_weather_data(self):
        weather = await self._fetch_weather()

        # Print current temperature
        print(weather.temperature)

        # Print daily forecasts
        for daily in weather:
            print(daily)

            # Print hourly forecasts
            for hourly in daily:
                print(f' --> {hourly!r}')

# Example usage
if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    client = WeatherClient("Münster")
    client.get_weather()
