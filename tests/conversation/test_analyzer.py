from app.conversation.analyzer import MessageAnalyzer


def test_normal_message_has_no_financial_risk():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "Привет :) Как прошел твой день?"
    )

    assert result.risk.money_focus == 0.0
    assert result.risk.pressure_score == 0.0
    assert result.risk.manipulation_score == 0.0
    assert result.risk.scam_probability == 0.0


def test_question_about_income_increases_money_focus():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "А ты хорошо зарабатываешь?"
    )

    assert result.risk.money_focus > 0.0
    assert result.risk.scam_probability == 0.0


def test_request_for_money_increases_money_focus():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "Можешь одолжить мне денег?"
    )

    assert result.risk.money_focus > 0.0


def test_emotional_pressure_is_detected():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "Если ты действительно заинтересован, ты бы помог мне."
    )

    assert result.risk.pressure_score > 0.0


def test_manipulation_is_detected():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "Если я тебе нравлюсь, докажи это."
    )

    assert result.risk.manipulation_score > 0.0


def test_money_plus_pressure_increases_scam_probability():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "Если ты действительно заинтересован, переведи мне деньги сейчас."
    )

    assert result.risk.money_focus > 0.0
    assert result.risk.pressure_score > 0.0
    assert result.risk.scam_probability > 0.0


def test_urgent_money_request_is_high_risk():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "Мне срочно нужны деньги, переведи сейчас."
    )

    assert result.risk.money_focus > 0.0
    assert result.risk.scam_probability > 0.0


def test_signals_are_returned():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "Если ты меня любишь, переведи деньги."
    )

    signal_names = {signal.name for signal in result.signals}

    assert "money_focus" in signal_names
    assert "manipulation" in signal_names
    assert "scam" in signal_names


def test_interest_signal_is_detected():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "Ты мне очень нравишься"
    )

    signal_names = {signal.name for signal in result.positive_signals}

    assert "interest" in signal_names


def test_mutuality_signal_is_detected():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "Я тоже хочу тебя увидеть"
    )

    signal_names = {signal.name for signal in result.positive_signals}

    assert "mutuality" in signal_names


def test_comfort_signal_is_detected():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "Мне очень комфортно с тобой"
    )

    signal_names = {signal.name for signal in result.positive_signals}

    assert "comfort" in signal_names


def test_flirt_signal_is_detected():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "Ты очень привлекательный мужчина"
    )

    signal_names = {signal.name for signal in result.positive_signals}

    assert "flirt" in signal_names


def test_explicit_meeting_proposal_is_detected():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "Давай встретимся завтра"
    )

    signal_names = {signal.name for signal in result.positive_signals}

    assert "meeting" in signal_names


def test_future_meeting_context_is_not_meeting_signal():
    analyzer = MessageAnalyzer()

    result = analyzer.analyze(
        "Когда будем ехать я буду писать"
    )

    signal_names = {signal.name for signal in result.positive_signals}

    assert "meeting" not in signal_names
