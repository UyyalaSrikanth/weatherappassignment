import asyncio
from pathlib import Path

from weather_orders.order_processing import process_orders


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    orders_path = base_dir / "orders.json"
    env_path = base_dir / ".env"

    asyncio.run(process_orders(orders_path=str(orders_path), env_path=str(env_path)))
    print("Success: Weather-based order update completed.")


if __name__ == "__main__":
    main()
