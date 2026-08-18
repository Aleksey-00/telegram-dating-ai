from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.conversation.enums import MessageSender
from app.database.models import Message


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        conversation_id: int,
        sender: MessageSender,
        text: str,
        telegram_message_id: int | None = None,
        metadata: dict | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            sender=sender,
            text=text,
            telegram_message_id=telegram_message_id,
            metadata_=metadata,
        )

        self.session.add(message)

        await self.session.flush()

        return message

    async def get_recent(
        self,
        conversation_id: int,
        limit: int = 50,
    ) -> list[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        return list(reversed(result.scalars().all()))
