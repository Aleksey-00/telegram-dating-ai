from app.ai.profile import get_user_profile
from app.ai.prompts import SYSTEM_PROMPT
from app.conversation.engine import ConversationResult
from app.conversation.enums import MessageSender
from app.database.models import Conversation, Message


class AIContextBuilder:
    def build(
        self,
        *,
        conversation: Conversation,
        messages: list[Message],
        result: ConversationResult,
    ) -> list[dict[str, str]]:
        system_prompt = self._build_system_prompt(
            conversation=conversation,
            result=result,
        )

        history = self._build_history(messages)

        return [
            {
                "role": "system",
                "content": system_prompt,
            },
            *history,
        ]

    @staticmethod
    def _build_system_prompt(
        *,
        conversation: Conversation,
        result: ConversationResult,
    ) -> str:
        state = result.state
        risk = result.risk

        context = f"""
Контекст конкретного общения:

Собеседница:
Имя: {conversation.display_name or "неизвестно"}
Username: {conversation.username or "неизвестно"}

Стадия общения: {state.stage.value}

Показатели:
- интерес: {state.interest_score:.2f}
- взаимность: {state.mutuality_score:.2f}
- комфорт: {state.comfort_score:.2f}
- флирт: {state.flirt_score:.2f}
- готовность к встрече: {state.meeting_readiness:.2f}

Риски:
- вероятность мошенничества: {risk.scam_probability:.2f}
- финансовый интерес: {risk.money_focus:.2f}
- манипуляция: {risk.manipulation_score:.2f}
- давление: {risk.pressure_score:.2f}

Решение системы:
{result.decision.decision.value}

Используй эти данные как дополнительный контекст.
Не упоминай эти показатели в сообщении собеседнице.
""".strip()

        profile = get_user_profile()

        return (
            f"{SYSTEM_PROMPT.strip()}\n\n"
            f"{profile.to_prompt()}\n\n"
            f"{context}"
        )

    @staticmethod
    def _build_history(
        messages: list[Message],
    ) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []

        for message in messages:
            role = (
                "assistant"
                if message.sender == MessageSender.ME
                else "user"
            )

            result.append(
                {
                    "role": role,
                    "content": message.text,
                }
            )

        return result
