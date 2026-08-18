from dataclasses import dataclass, field
import re

from app.conversation.risk import RiskAssessment


@dataclass(slots=True)
class RiskSignal:
    name: str
    score: float
    reason: str


@dataclass(slots=True)
class MessageAnalysis:
    risk: RiskAssessment
    signals: list[RiskSignal] = field(default_factory=list)


class MessageAnalyzer:
    """
    Детерминированный анализ одного сообщения.

    Это первый слой анализа.
    Он не принимает окончательное решение STOP/CONTINUE.
    Окончательное решение принимает DecisionEngine.
    """

    MONEY_PATTERNS = (
        r"\bденьг",
        r"\bзарплат",
        r"\bдоход",
        r"\bзарабатыва",
        r"\bфинанс",
        r"\bкредит",
        r"\bдолг",
        r"\bперевод",
        r"\bпереведи",
        r"\bскинь",
        r"\bодолжи",
        r"\bпомоги.*деньг",
        r"\bоплат",
        r"\bкошел[её]к",
        r"\bкарта\b",
    )

    MONEY_REQUEST_PATTERNS = (
        r"\bодолжи(?:ть)?\s+мне",
        r"\bможешь\s+(?:мне\s+)?(?:одолжить|перевести|скинуть)",
        r"\bпереведи\s+(?:мне\s+)?деньги",
        r"\bскинь\s+(?:мне\s+)?деньги",
        r"\bдай\s+(?:мне\s+)?денег",
        r"\bпомоги\s+(?:мне\s+)?деньгами",
        r"\bможешь\s+помочь\s+(?:мне\s+)?деньгами",
    )

    PRESSURE_PATTERNS = (
        r"\bесли ты (?:меня )?действительно",
        r"\bесли бы ты действительно",
        r"\bдокажи.*(?:любов|чувств|серьез)",
        r"\bты должен",
        r"\bты обяз",
        r"\bнормальный мужчина",
        r"\bнастоящий мужчина",
        r"\bнеужели тебе жалко",
        r"\bтебе что.*жалко",
        r"\bесли тебе не жалко",
    )

    SCAM_PATTERNS = (
        r"\bсрочно\b",
        r"\bпрямо сейчас\b",
        r"\bнужно.*деньг",
        r"\bнужны.*деньг",
        r"\bпополн",
        r"\bпереведи.*(?:срочно|сейчас)",
        r"\bскинь.*(?:срочно|сейчас)",
        r"\bоплати.*(?:сейчас|срочно)",
    )

    MANIPULATION_PATTERNS = (
        r"\bесли ты меня любишь",
        r"\bесли я тебе нравлюсь",
        r"\bдокажи.*(?:любов|отношени)",
        r"\bнастоящий мужчина",
        r"\bнормальный мужчина",
        r"\bты меня разочаровал",
        r"\bты меня разочаровываешь",
        r"\bзначит тебе всё равно",
        r"\bзначит я тебе не нужна",
    )

    def analyze(self, text: str) -> MessageAnalysis:
        normalized = self._normalize(text)

        money_score = self._score_matches(
            normalized,
            self.MONEY_PATTERNS,
            per_match=0.15,
            maximum=1.0,
        )

        money_request_score = self._score_matches(
            normalized,
            self.MONEY_REQUEST_PATTERNS,
            per_match=0.80,
            maximum=1.0,
        )

        money_score = max(
            money_score,
            money_request_score,
        )

        pressure_score = self._score_matches(
            normalized,
            self.PRESSURE_PATTERNS,
            per_match=0.30,
            maximum=1.0,
        )

        manipulation_score = self._score_matches(
            normalized,
            self.MANIPULATION_PATTERNS,
            per_match=0.30,
            maximum=1.0,
        )

        scam_score = self._score_matches(
            normalized,
            self.SCAM_PATTERNS,
            per_match=0.35,
            maximum=1.0,
        )

        # Сильная комбинация финансового интереса + давления
        # является более подозрительной, чем каждый сигнал отдельно.
        if money_score >= 0.30 and (
            pressure_score >= 0.30
            or manipulation_score >= 0.30
        ):
            scam_score = min(1.0, scam_score + 0.20)

        signals: list[RiskSignal] = []

        if money_score > 0:
            signals.append(
                RiskSignal(
                    name="money_focus",
                    score=money_score,
                    reason="В сообщении обнаружены признаки финансового интереса.",
                )
            )

        if pressure_score > 0:
            signals.append(
                RiskSignal(
                    name="pressure",
                    score=pressure_score,
                    reason="Обнаружены признаки давления на собеседника.",
                )
            )

        if manipulation_score > 0:
            signals.append(
                RiskSignal(
                    name="manipulation",
                    score=manipulation_score,
                    reason="Обнаружены признаки эмоциональной манипуляции.",
                )
            )

        if scam_score > 0:
            signals.append(
                RiskSignal(
                    name="scam",
                    score=scam_score,
                    reason="Обнаружены признаки потенциально мошеннического поведения.",
                )
            )

        risk = RiskAssessment(
            scam_probability=scam_score,
            money_focus=money_score,
            manipulation_score=manipulation_score,
            pressure_score=pressure_score,
        )

        return MessageAnalysis(
            risk=risk,
            signals=signals,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    @staticmethod
    def _score_matches(
        text: str,
        patterns: tuple[str, ...],
        *,
        per_match: float,
        maximum: float,
    ) -> float:
        matches = sum(
            1
            for pattern in patterns
            if re.search(pattern, text, flags=re.IGNORECASE)
        )

        return min(maximum, matches * per_match)
