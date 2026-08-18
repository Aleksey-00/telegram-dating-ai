from app.conversation.analyzer import MessageAnalysis
from app.conversation.enums import ConversationStage
from app.conversation.state import ConversationState


class ConversationStateUpdater:
    """
    Обновляет состояние общения после анализа сообщения.

    Пока используется простая эвристическая модель.
    Позже сюда подключим LLM.
    """

    def update(
        self,
        state: ConversationState,
        analysis: MessageAnalysis,
    ) -> ConversationState:
        text = analysis

        risk = text.risk

        # Пока risk-анализ не содержит positive signals,
        # поэтому используем отсутствие риска как слабый
        # индикатор нормального общения.
        if (
            risk.money_focus == 0.0
            and risk.pressure_score == 0.0
            and risk.manipulation_score == 0.0
            and risk.scam_probability == 0.0
        ):
            state.interest_score = min(
                1.0,
                state.interest_score + 0.05,
            )

            state.mutuality_score = min(
                1.0,
                state.mutuality_score + 0.05,
            )

            state.comfort_score = min(
                1.0,
                state.comfort_score + 0.05,
            )

        state.meeting_readiness = self._calculate_meeting_readiness(
            state,
        )

        state.stage = self._calculate_stage(state)

        return state

    @staticmethod
    def _calculate_meeting_readiness(
        state: ConversationState,
    ) -> float:
        score = (
            state.interest_score * 0.30
            + state.mutuality_score * 0.30
            + state.comfort_score * 0.25
            + state.flirt_score * 0.15
        )

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
