from app.conversation.engine import ConversationEngine
from app.conversation.enums import ConversationDecision, ConversationStage


def test_positive_conversation_reaches_meeting():
    engine = ConversationEngine()

    messages = [
        "Привет, как прошёл твой день?",
        "Мне интересно с тобой",
        "Я тоже хочу тебя увидеть",
        "Мне очень комфортно с тобой",
        "Ты очень привлекательный мужчина",
        "Давай встретимся завтра",
    ]

    results = []

    for text in messages:
        results.append(
            engine.process_message(text)
        )

    result = results[-1]

    assert result.analysis.positive_signals

    assert result.state.interest_score > 0.0
    assert result.state.mutuality_score > 0.0
    assert result.state.comfort_score > 0.0
    assert result.state.flirt_score > 0.0

    assert result.state.meeting_readiness >= 0.75

    assert result.state.stage == ConversationStage.MEETING

    assert (
        result.decision.decision
        == ConversationDecision.SUGGEST_MEETING
    )
