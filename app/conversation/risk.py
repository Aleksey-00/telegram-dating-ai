from dataclasses import dataclass


@dataclass(slots=True)
class RiskAssessment:
    scam_probability: float = 0.0
    money_focus: float = 0.0
    manipulation_score: float = 0.0
    inconsistency_score: float = 0.0
    pressure_score: float = 0.0

    def __post_init__(self) -> None:
        self._validate_scores()

    def _validate_scores(self) -> None:
        scores = {
            "scam_probability": self.scam_probability,
            "money_focus": self.money_focus,
            "manipulation_score": self.manipulation_score,
            "inconsistency_score": self.inconsistency_score,
            "pressure_score": self.pressure_score,
        }

        for name, value in scores.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0.0 and 1.0, got {value}"
                )
