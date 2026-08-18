from types import SimpleNamespace

from app.ai.context import AIContextBuilder
from app.ai.prompts import SYSTEM_PROMPT
from app.conversation.enums import (
    ConversationDecision,
    ConversationStage,
    MessageSender,
)
from app.conversation.risk import RiskAssessment
from app.conversation.state import ConversationState


def test_ai_context_contains_system_prompt_and_state():
    builder = AIContextBuilder()

    conversation = SimpleNamespace(
        display_name="Анна",
        username="anna",
    )

    result = SimpleNamespace(
        state=ConversationState(
            stage=ConversationStage.COMFORT,
            interest_score=0.7,
            mutuality_score=0.6,
            comfort_score=0.8,
            flirt_score=0.4,
            meeting_readiness=0.65,
        ),
        risk=RiskAssessment(),
        decision=SimpleNamespace(
            decision=ConversationDecision.CONTINUE,
        ),
    )

    messages = [
        SimpleNamespace(
            sender=MessageSender.HER,
            text="Мне нравится путешествовать",
        ),
        SimpleNamespace(
            sender=MessageSender.ME,
            text="Я тоже люблю путешествия",
        ),
    ]

    context = builder.build(
        conversation=conversation,
        messages=messages,
        result=result,
    )

    assert context[0]["role"] == "system"
    assert SYSTEM_PROMPT.strip() in context[0]["content"]
    assert "Анна" in context[0]["content"]
    assert "comfort" in context[0]["content"]
    assert "0.65" in context[0]["content"]

    assert context[1] == {
        "role": "user",
        "content": "Мне нравится путешествовать",
    }

    assert context[2] == {
        "role": "assistant",
        "content": "Я тоже люблю путешествия",
    }
