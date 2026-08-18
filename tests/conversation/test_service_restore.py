import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import get_settings
from app.conversation.enums import ConversationDecision, MessageSender
from app.conversation.service import ConversationService
from app.database.models import Conversation, ConversationAssessment, Message


@pytest.mark.asyncio
async def test_conversation_service_restores_and_accumulates_risk():
    settings = get_settings()

    engine = create_async_engine(
        settings.database_url,
        echo=False,
    )

    SessionLocal = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    telegram_user_id = 987654325

    try:
        # Первый экземпляр сервиса.
        async with SessionLocal() as session:
            service = ConversationService(session)

            result, conversation_id = await service.process_message(
                telegram_user_id=telegram_user_id,
                text="Можешь одолжить мне денег?",
                sender=MessageSender.HER,
            )

            await session.commit()

            assert result.decision.decision == ConversationDecision.CAUTION
            assert result.risk.money_focus >= 0.80

        # Имитируем перезапуск приложения:
        # новый session + новый ConversationService.
        async with SessionLocal() as session:
            service = ConversationService(session)

            result, restored_conversation_id = await service.process_message(
                telegram_user_id=telegram_user_id,
                text="Если ты меня любишь, ты бы помог.",
                sender=MessageSender.HER,
            )

            await session.commit()

            assert restored_conversation_id == conversation_id

            # money_focus из первого сообщения восстановлен.
            assert result.risk.money_focus >= 0.80

            # Второе сообщение добавило manipulation.
            assert result.risk.manipulation_score >= 0.30

            # Решение всё ещё должно учитывать накопленный риск.
            assert result.decision.decision == ConversationDecision.CAUTION

        # Ещё один перезапуск.
        async with SessionLocal() as session:
            service = ConversationService(session)

            result, restored_conversation_id = await service.process_message(
                telegram_user_id=telegram_user_id,
                text=(
                    "Докажи, что ты настоящий мужчина, "
                    "переведи деньги сейчас."
                ),
                sender=MessageSender.HER,
            )

            await session.commit()

            assert restored_conversation_id == conversation_id

            # Накопленные признаки не должны исчезнуть.
            assert result.risk.money_focus >= 0.80
            assert result.risk.manipulation_score >= 0.30
            assert result.risk.pressure_score >= 0.30

            # Финальное сообщение содержит scam-признак.
            assert result.risk.scam_probability > 0.0

            # На текущих порогах это должно привести к STOP.
            assert result.decision.decision == ConversationDecision.STOP

            conversation = await session.get(
                Conversation,
                conversation_id,
            )

            assert conversation is not None
            assert conversation.decision == ConversationDecision.STOP.value

            assessments = (
                await session.execute(
                    select(ConversationAssessment)
                    .where(
                        ConversationAssessment.conversation_id
                        == conversation_id
                    )
                    .order_by(ConversationAssessment.id)
                )
            ).scalars().all()

            assert len(assessments) == 3

            assert assessments[-1].decision == ConversationDecision.STOP.value

            messages = (
                await session.execute(
                    select(Message)
                    .where(
                        Message.conversation_id == conversation_id
                    )
                    .order_by(Message.id)
                )
            ).scalars().all()

            assert len(messages) == 3

            await session.delete(conversation)
            await session.commit()

    finally:
        await engine.dispose()
