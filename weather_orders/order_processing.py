import asyncio
import json
from pathlib import Path
from typing import Any

import aiohttp

from weather_orders.config import load_settings, Settings
from weather_orders.logger import setup_logger
from weather_orders.openweather_client import OpenWeatherError, fetch_weather_main


DELAYED_WEATHER = {"Rain", "Snow", "Extreme"}


def _build_delayed_message(customer: str, city: str, weather_main: str) -> str:
    weather_lower = weather_main.lower()
    return (
        f"Hi {customer}, your order to {city} is delayed due to {weather_lower}. "
        "We appreciate your patience!"
    )


def _build_on_track_message(customer: str, city: str) -> str:
    return (
        f"Hi {customer}, your order to {city} is on track. "
        "We appreciate your patience!"
    )


def _build_error_message(customer: str, city: str) -> str:
    return (
        f"Hi {customer}, we are experiencing an issue checking weather for {city} right now. "
        "Your order status will be updated as soon as we can. We appreciate your patience!"
    )


def _read_orders(orders_path: Path) -> list[dict[str, Any]]:
    return json.loads(orders_path.read_text(encoding="utf-8"))


def _write_orders(orders_path: Path, orders: list[dict[str, Any]]) -> None:
    orders_path.write_text(json.dumps(orders, indent=2), encoding="utf-8")


async def _process_one_order(
    order: dict[str, Any],
    *,
    session: aiohttp.ClientSession,
    settings: Settings,
    logger,
) -> dict[str, Any]:
    customer = str(order.get("customer", "")).strip()
    city = str(order.get("city", "")).strip()
    order_id = str(order.get("order_id", "")).strip()

    try:
        weather_main = await fetch_weather_main(session, settings, city)

        if weather_main in DELAYED_WEATHER:
            order["status"] = "Delayed"
            order["message"] = _build_delayed_message(customer, city, weather_main)
        else:
            # For other weather types, we mark the order as on time.
            order["status"] = "On Time"
            order["message"] = _build_on_track_message(customer, city)

        logger.info(f"order_id={order_id} city={city} weather={weather_main}")
        return order

    except OpenWeatherError as exc:
        # Invalid city (like InvalidCity123) should not crash the whole script.
        logger.error(f"order_id={order_id} city={city} OpenWeatherError: {exc}")
        order["status"] = "Error"
        order["message"] = _build_error_message(customer, city)
        return order
    except Exception as exc:  # Catch-all to prevent one failure from stopping all.
        logger.error(f"order_id={order_id} city={city} unexpected error: {exc}")
        order["status"] = "Error"
        order["message"] = _build_error_message(customer, city)
        return order


async def process_orders(orders_path: str = "orders.json", env_path: str = ".env") -> None:
    """
    Load orders, fetch all city weather in parallel, then write back updated orders.json.
    """

    logger = setup_logger()
    settings = load_settings(env_path=env_path)

    orders_file = Path(orders_path)
    orders = _read_orders(orders_file)

    timeout = aiohttp.ClientTimeout(total=25)
    headers = {
        # Beginner-friendly: a basic user-agent helps with some environments.
        "User-Agent": "weather-orders/1.0",
    }

    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        # Build tasks for ALL orders so they run concurrently.
        tasks = [
            _process_one_order(
                order.copy(), session=session, settings=settings, logger=logger
            )
            for order in orders
        ]

        updated_orders = await asyncio.gather(*tasks)

    _write_orders(orders_file, updated_orders)
    logger.info(f"Updated {orders_file.resolve()}")

