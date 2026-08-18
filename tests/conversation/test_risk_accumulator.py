from app.conversation.risk_accumulator import RiskAccumulator


def test_risk_accumulates_across_messages():
    accumulator = RiskAccumulator()

    accumulator.add_message(
        "А ты хорошо зарабатываешь?"
    )

    first_money_score = accumulator.risk.money_focus

    accumulator.add_message(
        "Можешь одолжить мне денег?"
    )

    second_money_score = accumulator.risk.money_focus

    assert first_money_score > 0.0
    assert second_money_score > first_money_score


def test_multiple_risky_messages_increase_scam_risk():
    accumulator = RiskAccumulator()

    accumulator.add_message(
        "А ты хорошо зарабатываешь?"
    )

    first_score = accumulator.risk.scam_probability

    accumulator.add_message(
        "Если ты действительно заинтересован, помоги мне деньгами."
    )

    second_score = accumulator.risk.scam_probability

    assert second_score > first_score


def test_risk_cannot_exceed_one():
    accumulator = RiskAccumulator()

    for _ in range(20):
        accumulator.add_message(
            "Мне срочно нужны деньги, переведи сейчас."
        )

    assert accumulator.risk.scam_probability <= 1.0
    assert accumulator.risk.money_focus <= 1.0
    assert accumulator.risk.pressure_score <= 1.0
    assert accumulator.risk.manipulation_score <= 1.0


def test_normal_conversation_does_not_increase_risk():
    accumulator = RiskAccumulator()

    accumulator.add_message(
        "Привет! Как прошел твой день?"
    )

    accumulator.add_message(
        "Что сегодня интересного делала?"
    )

    assert accumulator.risk.scam_probability == 0.0
    assert accumulator.risk.money_focus == 0.0
    assert accumulator.risk.pressure_score == 0.0
    assert accumulator.risk.manipulation_score == 0.0
