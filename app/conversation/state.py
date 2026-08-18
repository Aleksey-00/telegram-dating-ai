from dataclasses import dataclass

from app.conversation.enums import ConversationStage


@dataclass(slots=True)
class ConversationState:
    stage: ConversationStage = ConversationStage.INTEREST

    interest_score: float = 0.0
    mutuality_score: float = 0.0
    comfort_score: float = 0.0
    flirt_score: float = 0.0
    meeting_readiness: float = 0.0

    def __post_init__(self) -> None:
        self._validate_scores()

    def _validate_scores(self) -> None:
        scores = {
            "interest_score": self.interest_score,
            "mutuality_score": self.mutuality_score,
            "comfort_score": self.comfort_score,
            "flirt_score": self.flirt_score,
            "meeting_readiness": self.meeting_readiness,
        }

        for name, value in scores.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0.0 and 1.0, got {value}"
                )
