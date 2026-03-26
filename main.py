"""
Async Weather-Based Order Updates

This script:
- Reads `orders.json`
- Fetches weather for all order cities concurrently using OpenWeatherMap
- If the weather is Rain/Snow/Extreme, updates the order status to `Delayed`
- Writes back `orders.json` with an added `message` field

Run:
  1) Ensure a `.env` file exists in this folder with `OPENWEATHER_API_KEY`
  2) Install deps: `pip install -r requirements.txt`
  3) Run: `python main.py`
"""

import asyncio
from pathlib import Path

from weather_orders.order_processing import process_orders


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    orders_path = base_dir / "orders.json"
    env_path = base_dir / ".env"

    # Start the async workflow.
    asyncio.run(process_orders(orders_path=str(orders_path), env_path=str(env_path)))


if __name__ == "__main__":
    main()
