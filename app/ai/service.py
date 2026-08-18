from app.ai.client import AIClient, AIMessage
from app.ai.context import AIContextBuilder
from app.conversation.engine import ConversationResult
from app.database.models import Conversation
from app.database.repositories.message import MessageRepository


class ConversationAIService:
    def __init__(
        self,
        *,
        client: AIClient | None = None,
        context_builder: AIContextBuilder | None = None,
        messages: MessageRepository,
    ) -> None:
        self.client = client or AIClient()
        self.context_builder = (
            context_builder or AIContextBuilder()
        )
        self.messages = messages

    async def generate_reply(
        self,
        *,
        conversation: Conversation,
        result: ConversationResult,
    ) -> str:
        history = await self.messages.get_recent(
            conversation.id,
            limit=50,
        )

        context = self.context_builder.build(
            conversation=conversation,
            messages=history,
            result=result,
        )

        messages = [
            AIMessage(
                role=item["role"],
                content=item["content"],
            )
            for item in context
        ]

        return await self.client.generate(
            messages,
            temperature=0.8,
            max_tokens=500,
        )
