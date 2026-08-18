import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import get_settings
from app.conversation.enums import MessageSender
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

    telegram_user_id = 987654324

    try:
        # Первый экземпляр сервиса.
        async with SessionLocal() as session:
            service = ConversationService(session)

            result, conversation_id = await service.process_message(
                telegram_user_id=telegram_user_id,
                text="У меня сейчас проблемы с финансами",
                sender=MessageSender.HER,
            )

            await session.commit()

            assert result.risk.money_focus == 0.15

        # Новый session + новый ConversationService.
        # Имитируем перезапуск приложения.
        async with SessionLocal() as session:
            service = ConversationService(session)

            result, restored_conversation_id = await service.process_message(
                telegram_user_id=telegram_user_id,
                text="У меня сейчас проблемы с финансами",
                sender=MessageSender.HER,
            )

            await session.commit()

            assert restored_conversation_id == conversation_id

            # Первые 0.15 были восстановлены из БД.
            # Второе сообщение добавило ещё 0.15.
            assert result.risk.money_focus == 0.30

            conversation = await session.get(
                Conversation,
                conversation_id,
            )

            assert conversation is not None

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

            assert len(assessments) == 2
            assert assessments[0].money_focus == 0.15
            assert assessments[1].money_focus == 0.30

            messages = (
                await session.execute(
                    select(Message)
                    .where(
                        Message.conversation_id == conversation_id
                    )
                )
            ).scalars().all()

            assert len(messages) == 2

            await session.delete(conversation)
            await session.commit()

    finally:
        await engine.dispose()
