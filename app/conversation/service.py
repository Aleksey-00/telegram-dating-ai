from sqlalchemy.ext.asyncio import AsyncSession

from app.conversation.engine import ConversationEngine, ConversationResult
from app.conversation.enums import ConversationStage, MessageSender
from app.conversation.risk import RiskAssessment
from app.conversation.state import ConversationState
from app.database.models import Conversation, ConversationAssessment
from app.database.repositories.conversation import ConversationRepository
from app.database.repositories.conversation_assessment import (
    ConversationAssessmentRepository,
)
from app.database.repositories.message import MessageRepository


class ConversationService:
    def __init__(
        self,
        session: AsyncSession,
        engine: ConversationEngine | None = None,
    ):
        self.session = session
        self.engine = engine or ConversationEngine()

        self.conversations = ConversationRepository(session)
        self.messages = MessageRepository(session)
        self.assessments = ConversationAssessmentRepository(session)

    async def _restore_engine_state(
        self,
        conversation: Conversation,
    ) -> None:
        assessment = await self.assessments.get_latest(
            conversation.id
        )

        if assessment is None:
            return

        self.engine.state = ConversationState(
            stage=ConversationStage(conversation.stage),
            interest_score=assessment.interest_score,
            mutuality_score=assessment.mutuality_score,
            comfort_score=assessment.comfort_score,
            flirt_score=assessment.flirt_score,
            meeting_readiness=assessment.meeting_readiness,
        )

        self.engine.accumulator.restore(
            RiskAssessment(
                scam_probability=assessment.scam_probability,
                money_focus=assessment.money_focus,
                manipulation_score=assessment.manipulation_score,
                inconsistency_score=assessment.inconsistency_score,
                pressure_score=assessment.pressure_score,
            )
        )

    async def process_message(
        self,
        *,
        telegram_user_id: int,
        text: str,
        sender: MessageSender,
        username: str | None = None,
        display_name: str | None = None,
        telegram_message_id: int | None = None,
    ) -> tuple[ConversationResult, int]:

        conversation = await self.conversations.get_or_create(
            telegram_user_id=telegram_user_id,
            username=username,
            display_name=display_name,
        )

        await self._restore_engine_state(conversation)

        await self.messages.create(
            conversation_id=conversation.id,
            sender=sender,
            text=text,
            telegram_message_id=telegram_message_id,
        )

        result = self.engine.process_message(text)

        conversation.stage = result.state.stage.value
        conversation.decision = result.decision.decision.value

        assessment = ConversationAssessment(
            conversation_id=conversation.id,
            interest_score=result.state.interest_score,
            mutuality_score=result.state.mutuality_score,
            comfort_score=result.state.comfort_score,
            flirt_score=result.state.flirt_score,
            meeting_readiness=result.state.meeting_readiness,
            scam_probability=result.risk.scam_probability,
            money_focus=result.risk.money_focus,
            manipulation_score=result.risk.manipulation_score,
            inconsistency_score=result.risk.inconsistency_score,
            pressure_score=result.risk.pressure_score,
            decision=result.decision.decision.value,
            reasons=result.decision.reasons,
            observations=[
                {
                    "name": signal.name,
                    "score": signal.score,
                    "reason": signal.reason,
                }
                for signal in result.analysis.signals
            ],
            positive_observations=[
                {
                    "name": signal.name,
                    "score": signal.score,
                    "reason": signal.reason,
                }
                for signal in result.analysis.positive_signals
            ],
        )

        self.session.add(assessment)

        await self.session.flush()

        return result, conversation.id
