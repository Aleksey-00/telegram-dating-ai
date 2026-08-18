import asyncio

from app.telegram.client import TelegramClientService
from app.telegram.handlers import register_handlers


async def main() -> None:
    telegram = TelegramClientService()

    register_handlers(telegram.client)

    await telegram.start()

    print("Telegram client started")

    try:
        await telegram.client.run_until_disconnected()
    finally:
        await telegram.stop()


if __name__ == "__main__":
    asyncio.run(main())
