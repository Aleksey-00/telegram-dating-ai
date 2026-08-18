from telethon import events

from app.conversation.enums import MessageSender
from app.conversation.service import ConversationService
from app.database.session import AsyncSessionLocal


def register_handlers(client) -> None:
    @client.on(events.NewMessage(incoming=True))
    async def handle_message(event) -> None:
        if event.message is None:
            return

        if not event.is_private:
            return

        sender = await event.get_sender()

        if sender is None or getattr(sender, "bot", False):
            return

        telegram_user_id = event.sender_id

        if telegram_user_id is None:
            return

        username = getattr(sender, "username", None)
        display_name = " ".join(
            part
            for part in (
                getattr(sender, "first_name", None),
                getattr(sender, "last_name", None),
            )
            if part
        ) or None

        text = event.message.message

        if not text:
            return

        async with AsyncSessionLocal() as session:
            service = ConversationService(session)

            result, conversation_id = await service.process_message(
                telegram_user_id=telegram_user_id,
                text=text,
                sender=MessageSender.HER,
                username=username,
                display_name=display_name,
                telegram_message_id=event.message.id,
            )

            await session.commit()

        print(
            f"[Telegram] conversation={conversation_id} "
            f"decision={result.decision.decision.value} "
            f"stage={result.state.stage.value}"
        )
