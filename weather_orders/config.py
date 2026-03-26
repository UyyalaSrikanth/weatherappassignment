import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    openweather_api_key: str
    openweather_base_url: str
    units: str


def load_settings(env_path: str = ".env") -> Settings:
    load_dotenv(env_path)

    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "Missing OPENWEATHER_API_KEY. Add it to the `.env` file."
        )

    return Settings(
        openweather_api_key=api_key,
        openweather_base_url="https://api.openweathermap.org",
        units="metric",
    )

