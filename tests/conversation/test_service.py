import pytest
from sqlalchemy import delete, select

from app.conversation.enums import ConversationDecision, MessageSender
from app.conversation.service import ConversationService
from app.database.models import Conversation, ConversationAssessment, Message
from app.database.session import AsyncSessionLocal


@pytest.mark.asyncio
async def test_conversation_service_persists_message_and_assessment():
    telegram_user_id = 987654321

    async with AsyncSessionLocal() as session:
        service = ConversationService(session)

        result, conversation_id = await service.process_message(
            telegram_user_id=telegram_user_id,
            username="test_user",
            display_name="Test User",
            text="Можешь одолжить мне денег?",
            sender=MessageSender.HER,
            telegram_message_id=12345,
        )

        await session.commit()

        assert result.decision.decision == ConversationDecision.CAUTION

        conversation = await session.get(
            Conversation,
            conversation_id,
        )

        assert conversation is not None
        assert conversation.telegram_user_id == telegram_user_id
        assert conversation.username == "test_user"
        assert conversation.display_name == "Test User"

        messages = (
            await session.execute(
                select(Message).where(
                    Message.conversation_id == conversation_id
                )
            )
        ).scalars().all()

        assert len(messages) == 1
        assert messages[0].text == "Можешь одолжить мне денег?"
        assert messages[0].sender == MessageSender.HER.value
        assert messages[0].telegram_message_id == 12345

        assessments = (
            await session.execute(
                select(ConversationAssessment).where(
                    ConversationAssessment.conversation_id
                    == conversation_id
                )
            )
        ).scalars().all()

        assert len(assessments) == 1

        assessment = assessments[0]

        assert assessment.money_focus >= 0.80
        assert assessment.decision == ConversationDecision.CAUTION.value

        await session.execute(
            delete(Conversation).where(
                Conversation.id == conversation_id
            )
        )

        await session.commit()

@pytest.mark.asyncio
async def test_conversation_service_persists_positive_observations():
    telegram_user_id = 987654322

    async with AsyncSessionLocal() as session:
        service = ConversationService(session)

        result, conversation_id = await service.process_message(
            telegram_user_id=telegram_user_id,
            username="positive_test_user",
            display_name="Positive Test User",
            text="Ты мне очень нравишься",
            sender=MessageSender.HER,
            telegram_message_id=12346,
        )

        await session.commit()

        assert result.analysis.positive_signals

        assessments = (
            await session.execute(
                select(ConversationAssessment).where(
                    ConversationAssessment.conversation_id
                    == conversation_id
                )
            )
        ).scalars().all()

        assert len(assessments) == 1

        assessment = assessments[0]

        assert assessment.positive_observations is not None
        assert len(assessment.positive_observations) > 0

        assert any(
            observation["name"] == "interest"
            for observation in assessment.positive_observations
        )

        await session.execute(
            delete(Conversation).where(
                Conversation.id == conversation_id
            )
        )

        await session.commit()

