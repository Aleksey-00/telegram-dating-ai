from telethon import TelegramClient

from app.config import get_settings


class TelegramClientService:
    def __init__(self) -> None:
        settings = get_settings()

        if settings.telegram_api_id is None:
            raise ValueError("TELEGRAM_API_ID is not configured")

        if not settings.telegram_api_hash:
            raise ValueError("TELEGRAM_API_HASH is not configured")

        self.client = TelegramClient(
            "telegram_dating_ai",
            settings.telegram_api_id,
            settings.telegram_api_hash,
        )

    async def start(self) -> None:
        await self.client.start()

    async def stop(self) -> None:
        await self.client.disconnect()
