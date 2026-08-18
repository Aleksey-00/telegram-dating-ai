from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.conversation.enums import (
    ConversationDecision,
    ConversationStage,
)
from app.database.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_user_id: Mapped[int] = mapped_column(
        unique=True,
        index=True,
    )

    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    stage: Mapped[str] = mapped_column(
        String(32),
        default=ConversationStage.INTEREST,
    )

    decision: Mapped[str] = mapped_column(
        String(32),
        default=ConversationDecision.CONTINUE,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    assessments: Mapped[list["ConversationAssessment"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationAssessment.created_at",
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
    )

    telegram_message_id: Mapped[int | None] = mapped_column(
        nullable=True,
        index=True,
    )

    sender: Mapped[str] = mapped_column(
        String(16),
    )

    text: Mapped[str] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )

    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages",
    )


class ConversationAssessment(Base):
    __tablename__ = "conversation_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
    )

    interest_score: Mapped[float]
    mutuality_score: Mapped[float]
    comfort_score: Mapped[float]
    flirt_score: Mapped[float]
    meeting_readiness: Mapped[float]

    scam_probability: Mapped[float]
    money_focus: Mapped[float]
    manipulation_score: Mapped[float]
    inconsistency_score: Mapped[float]
    pressure_score: Mapped[float]

    decision: Mapped[str] = mapped_column(
        String(32),
    )

    reasons: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    observations: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    positive_observations: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    conversation: Mapped["Conversation"] = relationship(
        back_populates="assessments",
    )
