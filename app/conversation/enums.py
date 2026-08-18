from enum import StrEnum


class ConversationStage(StrEnum):
    INTEREST = "interest"
    MUTUALITY = "mutuality"
    COMFORT = "comfort"
    FLIRT = "flirt"
    MEETING = "meeting"


class ConversationDecision(StrEnum):
    CONTINUE = "continue"
    CAUTION = "caution"
    SUGGEST_MEETING = "suggest_meeting"
    STOP = "stop"


class MessageSender(StrEnum):
    ME = "me"
    HER = "her"
