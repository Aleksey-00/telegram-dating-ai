from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ConversationAssessment


class ConversationAssessmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_latest(
        self,
        conversation_id: int,
    ) -> ConversationAssessment | None:
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
