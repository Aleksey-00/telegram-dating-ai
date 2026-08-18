from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.conversation.enums import ConversationDecision, ConversationStage
from app.database.models import Conversation


class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_user_id(
        self,
        telegram_user_id: int,
    ) -> Conversation | None:
        result = await self.session.execute(
            select(Conversation).where(
                Conversation.telegram_user_id == telegram_user_id
            )
        )

        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        telegram_user_id: int,
        username: str | None = None,
        display_name: str | None = None,
    ) -> Conversation:
        conversation = await self.get_by_telegram_user_id(
            telegram_user_id
        )

        if conversation is not None:
            return conversation

        conversation = Conversation(
            telegram_user_id=telegram_user_id,
            username=username,
            display_name=display_name,
            stage=ConversationStage.INTEREST,
            decision=ConversationDecision.CONTINUE,
        )

        self.session.add(conversation)

        await self.session.flush()

        return conversation

    async def get_latest_assessment(
        self,
        conversation_id: int,
    ):
        from sqlalchemy import select

        from app.database.models import ConversationAssessment

        result = await self.session.execute(
            select(ConversationAssessment)
            .where(
                ConversationAssessment.conversation_id == conversation_id
            )
            .order_by(
                ConversationAssessment.created_at.desc(),
                ConversationAssessment.id.desc(),
            )
            .limit(1)
        )

        return result.scalar_one_or_none()
