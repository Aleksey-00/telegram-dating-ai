from dataclasses import dataclass, field

from app.conversation.analyzer import MessageAnalysis, MessageAnalyzer
from app.conversation.decision import DecisionEngine, DecisionResult
from app.conversation.risk import RiskAssessment
from app.conversation.risk_accumulator import RiskAccumulator
from app.conversation.state import ConversationState
from app.conversation.state_updater import ConversationStateUpdater


@dataclass(slots=True)
class ConversationEngine:
    analyzer: MessageAnalyzer = field(
        default_factory=MessageAnalyzer,
    )

    decision_engine: DecisionEngine = field(
        default_factory=DecisionEngine,
    )

    accumulator: RiskAccumulator = field(
        default_factory=RiskAccumulator,
    )

    state_updater: ConversationStateUpdater = field(
        default_factory=ConversationStateUpdater,
    )

    state: ConversationState = field(
        default_factory=ConversationState,
    )

    def process_message(
        self,
        text: str,
    ) -> "ConversationResult":
        analysis = self.analyzer.analyze(text)

        risk = self.accumulator.add(analysis)

        self.state = self.state_updater.update(
            self.state,
            analysis,
        )

        decision = self.decision_engine.decide(
            state=self.state,
            risk=risk,
        )

        return ConversationResult(
            analysis=analysis,
            risk=risk,
            decision=decision,
            state=self.state,
        )


@dataclass(slots=True)
class ConversationResult:
    analysis: MessageAnalysis
    risk: RiskAssessment
    decision: DecisionResult
    state: ConversationState
