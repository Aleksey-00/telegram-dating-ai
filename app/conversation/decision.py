from dataclasses import dataclass, field

from app.conversation.enums import ConversationDecision
from app.conversation.risk import RiskAssessment
from app.conversation.state import ConversationState


@dataclass(slots=True)
class DecisionResult:
    decision: ConversationDecision
    reasons: list[str] = field(default_factory=list)


class DecisionEngine:
    STOP_SCAM_THRESHOLD = 0.85
    STOP_PRESSURE_THRESHOLD = 0.90
    CAUTION_MONEY_THRESHOLD = 0.80
    CAUTION_MANIPULATION_THRESHOLD = 0.75
    MEETING_THRESHOLD = 0.75

    def decide(
        self,
        state: ConversationState,
        risk: RiskAssessment,
    ) -> DecisionResult:

        reasons: list[str] = []

        if risk.scam_probability >= self.STOP_SCAM_THRESHOLD:
            reasons.append(
                "Высокая вероятность мошеннического поведения."
            )
            return DecisionResult(
                decision=ConversationDecision.STOP,
                reasons=reasons,
            )

        if risk.pressure_score >= self.STOP_PRESSURE_THRESHOLD:
            reasons.append(
                "Обнаружен высокий уровень давления."
            )
            return DecisionResult(
                decision=ConversationDecision.STOP,
                reasons=reasons,
            )

        if risk.money_focus >= self.CAUTION_MONEY_THRESHOLD:
            reasons.append(
                "Повышенный интерес к финансовой стороне жизни."
            )

        if risk.manipulation_score >= self.CAUTION_MANIPULATION_THRESHOLD:
            reasons.append(
                "Обнаружены признаки манипулятивного поведения."
            )

        if reasons:
            return DecisionResult(
                decision=ConversationDecision.CAUTION,
                reasons=reasons,
            )

        if state.meeting_readiness >= self.MEETING_THRESHOLD:
            reasons.append(
                "Высокая готовность к предложению встречи."
            )
            return DecisionResult(
                decision=ConversationDecision.SUGGEST_MEETING,
                reasons=reasons,
            )

        return DecisionResult(
            decision=ConversationDecision.CONTINUE,
            reasons=["Продолжать естественное общение."],
        )
