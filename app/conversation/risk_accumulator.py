from dataclasses import dataclass

from app.conversation.analyzer import MessageAnalysis, MessageAnalyzer
from app.conversation.risk import RiskAssessment


@dataclass(slots=True)
class RiskAccumulator:
    """
    Накапливает риск по сообщениям.

    Новое сообщение влияет на текущую оценку,
    но одно сообщение не должно мгновенно превращать
    нормальный диалог в STOP.
    """

    risk: RiskAssessment | None = None

    def __post_init__(self) -> None:
        if self.risk is None:
            self.risk = RiskAssessment()

    def add(self, analysis: MessageAnalysis) -> RiskAssessment:
        assert self.risk is not None

        self.risk = RiskAssessment(
            scam_probability=self._accumulate(
                self.risk.scam_probability,
                analysis.risk.scam_probability,
            ),
            money_focus=self._accumulate(
                self.risk.money_focus,
                analysis.risk.money_focus,
            ),
            manipulation_score=self._accumulate(
                self.risk.manipulation_score,
                analysis.risk.manipulation_score,
            ),
            inconsistency_score=self.risk.inconsistency_score,
            pressure_score=self._accumulate(
                self.risk.pressure_score,
                analysis.risk.pressure_score,
            ),
        )

        return self.risk

    @staticmethod
    def _accumulate(current: float, new: float) -> float:
        """
        Накопление с ограничением 1.0.

        Чем больше подозрительных сигналов,
        тем выше итоговый риск.
        """
        return min(1.0, current + new)

    def add_message(
        self,
        text: str,
        analyzer: MessageAnalyzer | None = None,
    ) -> MessageAnalysis:
        analyzer = analyzer or MessageAnalyzer()

        analysis = analyzer.analyze(text)
        self.add(analysis)

        return analysis

    def restore(self, risk: RiskAssessment) -> None:
        """
        Восстанавливает накопленный риск из сохранённого состояния.
        """
        self.risk = RiskAssessment(
            scam_probability=risk.scam_probability,
            money_focus=risk.money_focus,
            manipulation_score=risk.manipulation_score,
            inconsistency_score=risk.inconsistency_score,
            pressure_score=risk.pressure_score,
        )
