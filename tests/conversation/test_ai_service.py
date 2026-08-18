from types import SimpleNamespace

import pytest

from app.ai.service import ConversationAIService
from app.conversation.enums import ConversationDecision
from app.conversation.risk import RiskAssessment
from app.conversation.state import ConversationState


class FakeAIClient:
    def __init__(self):
        self.messages = None

    async def generate(
        self,
        messages,
        *,
        temperature,
        max_tokens,
    ):
        self.messages = messages
        return "О, я тоже люблю путешествия 🙂"


class FakeMessageRepository:
    async def get_recent(self, conversation_id, limit=50):
        return [
            SimpleNamespace(
                sender="her",
                text="Мне нравится путешествовать",
            ),
            SimpleNamespace(
                sender="me",
                text="Куда ты ездила?",
            ),
        ]


@pytest.mark.asyncio
async def test_conversation_ai_service_generates_reply():
    client = FakeAIClient()

    service = ConversationAIService(
        client=client,
        messages=FakeMessageRepository(),
    )

    conversation = SimpleNamespace(
        id=1,
        display_name="Анна",
        username="anna",
    )

    result = SimpleNamespace(
        state=ConversationState(),
        risk=RiskAssessment(),
        decision=SimpleNamespace(
            decision=ConversationDecision.CONTINUE,
        ),
    )

    reply = await service.generate_reply(
        conversation=conversation,
        result=result,
    )

    assert reply == "О, я тоже люблю путешествия 🙂"

    assert client.messages is not None
    assert client.messages[0].role == "system"

    history = client.messages[1:]

    assert history[0].role == "user"
    assert history[0].content == "Мне нравится путешествовать"

    assert history[1].role == "assistant"
    assert history[1].content == "Куда ты ездила?"
