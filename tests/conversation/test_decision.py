from app.conversation.decision import DecisionEngine
from app.conversation.enums import ConversationDecision
from app.conversation.risk import RiskAssessment
from app.conversation.state import ConversationState


def test_money_request_is_caution_not_stop():
    engine = DecisionEngine()

    result = engine.decide(
        state=ConversationState(),
        risk=RiskAssessment(
            money_focus=1.0,
        ),
    )

    assert result.decision == ConversationDecision.CAUTION


def test_manipulation_without_money_is_caution():
    engine = DecisionEngine()

    result = engine.decide(
        state=ConversationState(),
        risk=RiskAssessment(
            manipulation_score=0.30,
        ),
    )

    assert result.decision == ConversationDecision.CONTINUE


def test_money_and_manipulation_and_pressure_is_stop():
    engine = DecisionEngine()

    result = engine.decide(
        state=ConversationState(),
        risk=RiskAssessment(
            money_focus=1.0,
            manipulation_score=0.30,
            pressure_score=0.30,
            scam_probability=0.55,
        ),
    )

    assert result.decision == ConversationDecision.STOP


def test_high_scam_probability_is_stop():
    engine = DecisionEngine()

    result = engine.decide(
        state=ConversationState(),
        risk=RiskAssessment(
            scam_probability=0.85,
        ),
    )

    assert result.decision == ConversationDecision.STOP


def test_high_pressure_is_stop():
    engine = DecisionEngine()

    result = engine.decide(
        state=ConversationState(),
        risk=RiskAssessment(
            pressure_score=0.90,
        ),
    )

    assert result.decision == ConversationDecision.STOP
