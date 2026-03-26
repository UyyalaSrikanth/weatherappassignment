import aiohttp

from weather_orders.config import Settings


class OpenWeatherError(Exception):
    """Raised when OpenWeather returns an error response."""


async def fetch_weather_main(session: aiohttp.ClientSession, settings: Settings, city: str) -> str:
    """
    Fetch current weather for a city and return the `weather[0].main` value.

    Example returned values: "Rain", "Snow", "Clear", etc.
    """

    # OpenWeather current weather endpoint.
    url = f"{settings.openweather_base_url}/data/2.5/weather"

    params = {
        "q": city,
        "appid": settings.openweather_api_key,
        "units": settings.units,
    }

    async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
        if resp.status != 200:
            # Try to read the response body to log a helpful message.
            try:
                payload = await resp.json()
                message = payload.get("message", "").strip()
            except Exception:
                message = ""

            raise OpenWeatherError(f"OpenWeather status={resp.status} city={city} {message}".strip())

        payload = await resp.json()
        weather_list = payload.get("weather", [])
        if not weather_list:
            raise OpenWeatherError(f"OpenWeather returned no weather info for city={city}")

        main_value = weather_list[0].get("main", "")
        if not main_value:
            raise OpenWeatherError(f"OpenWeather returned empty weather[0].main for city={city}")

        return str(main_value)

