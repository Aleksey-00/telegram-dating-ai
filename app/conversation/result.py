from dataclasses import dataclass

from app.conversation.enums import (
    ConversationDecision,
    ConversationStage,
)


@dataclass(frozen=True)
class ConversationResult:
    decision: ConversationDecision
    stage: ConversationStage

    interest_score: float
    mutuality_score: float
    comfort_score: float
    flirt_score: float
    meeting_readiness: float

    scam_probability: float
    money_focus: float
    manipulation_score: float
    inconsistency_score: float
    pressure_score: float

    reasons: list[str]
    observations: list[str]
