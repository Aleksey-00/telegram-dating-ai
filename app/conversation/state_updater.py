from app.conversation.analyzer import MessageAnalysis
from app.conversation.enums import ConversationStage
from app.conversation.state import ConversationState


class ConversationStateUpdater:
    """
    Обновляет состояние общения после анализа сообщения.

    Positive signals увеличивают соответствующие показатели
    состояния разговора.
    """

    SIGNAL_WEIGHTS = {
        "interest": "interest_score",
        "mutuality": "mutuality_score",
        "comfort": "comfort_score",
        "flirt": "flirt_score",
    }

    NORMAL_MESSAGE_INCREMENT = 0.05
    MEETING_SIGNAL_INCREMENT = 0.25

    def update(
        self,
        state: ConversationState,
        analysis: MessageAnalysis,
    ) -> ConversationState:

        positive_names = {
            signal.name
            for signal in analysis.positive_signals
        }

        # Слабый прирост для обычного позитивного общения.
        if (
            not analysis.risk.money_focus
            and not analysis.risk.pressure_score
            and not analysis.risk.manipulation_score
            and not analysis.risk.scam_probability
            and not positive_names
        ):
            state.interest_score = min(
                1.0,
                state.interest_score + self.NORMAL_MESSAGE_INCREMENT,
            )

            state.mutuality_score = min(
                1.0,
                state.mutuality_score + self.NORMAL_MESSAGE_INCREMENT,
            )

            state.comfort_score = min(
                1.0,
                state.comfort_score + self.NORMAL_MESSAGE_INCREMENT,
            )

        for signal in analysis.positive_signals:
            field_name = self.SIGNAL_WEIGHTS.get(signal.name)

            if field_name is None:
                continue

            current = getattr(state, field_name)

            setattr(
                state,
                field_name,
                min(1.0, current + signal.score),
            )

        state.meeting_readiness = self._calculate_meeting_readiness(
            state,
            has_meeting_signal="meeting" in positive_names,
        )

        state.stage = self._calculate_stage(state)

        return state

    @classmethod
    def _calculate_meeting_readiness(
        cls,
        state: ConversationState,
        *,
        has_meeting_signal: bool = False,
    ) -> float:
        score = (
            state.interest_score * 0.30
            + state.mutuality_score * 0.30
            + state.comfort_score * 0.25
            + state.flirt_score * 0.15
        )

        if has_meeting_signal:
            score += cls.MEETING_SIGNAL_INCREMENT
            score = max(score, 0.75)

        return min(1.0, score)

    @staticmethod
    def _calculate_stage(
        state: ConversationState,
    ) -> ConversationStage:
        if state.meeting_readiness >= 0.75:
            return ConversationStage.MEETING

        if state.flirt_score >= 0.60:
            return ConversationStage.FLIRT

        if state.comfort_score >= 0.50:
            return ConversationStage.COMFORT

        if state.mutuality_score >= 0.30:
            return ConversationStage.MUTUALITY

        return ConversationStage.INTEREST
