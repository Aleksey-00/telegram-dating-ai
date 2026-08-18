from app.conversation.engine import ConversationEngine
from app.conversation.enums import ConversationDecision


def test_normal_conversation_continues():
    engine = ConversationEngine()

    result = engine.process_message(
        "Привет! Как прошел твой день?"
    )

    assert result.decision.decision == ConversationDecision.CONTINUE
    assert result.risk.scam_probability == 0.0


def test_money_request_causes_caution():
    engine = ConversationEngine()

    result = engine.process_message(
        "Можешь одолжить мне денег?"
    )

    assert result.decision.decision == ConversationDecision.CAUTION


def test_suspicious_pattern_can_stop_conversation():
    engine = ConversationEngine()

    messages = [
        "Ты хорошо зарабатываешь?",
        "Мне нужны деньги.",
        "Если ты действительно заинтересован, помоги мне.",
        "Мне срочно нужны деньги, переведи сейчас.",
    ]

    result = None

    for message in messages:
        result = engine.process_message(message)

    assert result is not None
    assert result.risk.scam_probability >= 0.85
    assert result.decision.decision == ConversationDecision.STOP


def test_normal_messages_increase_conversation_state():
    engine = ConversationEngine()

    for _ in range(10):
        result = engine.process_message(
            "Мне приятно с тобой общаться."
        )

    assert result.state.interest_score > 0.0
    assert result.state.mutuality_score > 0.0
    assert result.state.comfort_score > 0.0
