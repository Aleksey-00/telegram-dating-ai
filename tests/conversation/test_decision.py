import pytest

from app.conversation.decision import DecisionEngine
from app.conversation.enums import ConversationDecision
from app.conversation.risk import RiskAssessment
from app.conversation.state import ConversationState


@pytest.fixture
def engine() -> DecisionEngine:
    return DecisionEngine()


def test_normal_conversation_should_continue(
    engine: DecisionEngine,
) -> None:
    state = ConversationState(
        interest_score=0.6,
        mutuality_score=0.7,
        comfort_score=0.8,
        flirt_score=0.3,
        meeting_readiness=0.2,
    )

    risk = RiskAssessment()

    result = engine.decide(state, risk)

    assert result.decision == ConversationDecision.CONTINUE


def test_high_scam_probability_should_stop(
    engine: DecisionEngine,
) -> None:
    state = ConversationState()

    risk = RiskAssessment(
        scam_probability=0.91,
    )

    result = engine.decide(state, risk)

    assert result.decision == ConversationDecision.STOP


def test_high_money_focus_should_require_caution(
    engine: DecisionEngine,
) -> None:
    state = ConversationState()

    risk = RiskAssessment(
        money_focus=0.85,
    )

    result = engine.decide(state, risk)

    assert result.decision == ConversationDecision.CAUTION


def test_high_manipulation_should_require_caution(
    engine: DecisionEngine,
) -> None:
    state = ConversationState()

    risk = RiskAssessment(
        manipulation_score=0.80,
    )

    result = engine.decide(state, risk)

    assert result.decision == ConversationDecision.CAUTION


def test_high_meeting_readiness_should_suggest_meeting(
    engine: DecisionEngine,
) -> None:
    state = ConversationState(
        interest_score=0.8,
        mutuality_score=0.85,
        comfort_score=0.9,
        flirt_score=0.7,
        meeting_readiness=0.8,
    )

    risk = RiskAssessment()

    result = engine.decide(state, risk)

    assert result.decision == ConversationDecision.SUGGEST_MEETING


def test_invalid_score_should_raise_error() -> None:
    with pytest.raises(ValueError):
        ConversationState(
            interest_score=1.5,
        )

    with pytest.raises(ValueError):
        RiskAssessment(
            scam_probability=-0.1,
        )
