from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserProfile:
    """
    Факты о владельце Telegram-аккаунта.

    LLM может использовать только эти факты при ответах
    на вопросы о владельце.
    """

    name: str = ""
    age: int | None = None
    city: str = ""

    occupation: str = ""
    occupation_description: str = ""

    interests: tuple[str, ...] = ()
    books: tuple[str, ...] = ()

    travel_countries: tuple[str, ...] = ()
    travel_destination: str = ""
    travel_preferences: tuple[str, ...] = ()
    travel_interests: tuple[str, ...] = ()

    lifestyle: tuple[str, ...] = ()
    personality: tuple[str, ...] = ()

    dating_preferences: tuple[str, ...] = ()
    communication_style: tuple[str, ...] = ()
    relationship_goals: tuple[str, ...] = ()

    additional_context: str = ""

    def to_prompt(self) -> str:
        lines = [
            "ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:",
            f"Имя: {self.name or 'не указано'}",
            f"Возраст: {self.age if self.age is not None else 'не указан'}",
            f"Город: {self.city or 'не указан'}",
            f"Профессия: {self.occupation or 'не указана'}",
        ]

        if self.occupation_description:
            lines.append(
                f"О работе: {self.occupation_description}"
            )

        if self.interests:
            lines.append(
                "Интересы: " + ", ".join(self.interests)
            )

        if self.books:
            lines.append(
                "Книги: " + "; ".join(self.books)
            )

        if self.travel_countries:
            lines.append(
                "Страны, где был: "
                + ", ".join(self.travel_countries)
            )

        if self.travel_destination:
            lines.append(
                f"Хочет посетить: {self.travel_destination}"
            )

        if self.travel_preferences:
            lines.append(
                "Предпочтения в путешествиях: "
                + ", ".join(self.travel_preferences)
            )

        if self.travel_interests:
            lines.append(
                "Что нравится в путешествиях: "
                + ", ".join(self.travel_interests)
            )

        if self.lifestyle:
            lines.append(
                "Образ жизни: " + "; ".join(self.lifestyle)
            )

        if self.personality:
            lines.append(
                "Особенности характера и вкуса: "
                + "; ".join(self.personality)
            )

        if self.dating_preferences:
            lines.append(
                "Что привлекает в девушках: "
                + "; ".join(self.dating_preferences)
            )

        if self.communication_style:
            lines.append(
                "Предпочтительный стиль общения: "
                + "; ".join(self.communication_style)
            )

        if self.relationship_goals:
            lines.append(
                "Цели знакомства: "
                + "; ".join(self.relationship_goals)
            )

        if self.additional_context:
            lines.append(
                f"Дополнительная информация: "
                f"{self.additional_context}"
            )

        lines.extend(
            [
                "",
                "Правило профиля:",
                "Не выдумывай факты о пользователе.",
                "Если собеседница спрашивает о пользователе, "
                "используй только информацию из этого профиля.",
                "Если нужной информации нет, не придумывай её.",
            ]
        )

        return "\n".join(lines)


def _split_setting(value: str) -> tuple[str, ...]:
    return tuple(
        item.strip()
        for item in value.split(",")
        if item.strip()
    )


def get_user_profile() -> UserProfile:
    from app.config import get_settings

    settings = get_settings()

    return UserProfile(
        name=settings.user_name,
        age=settings.user_age,
        city=settings.user_city,
        occupation=settings.user_occupation,
        occupation_description=settings.user_occupation_description,
        interests=_split_setting(settings.user_interests),
        books=_split_setting(settings.user_books),
        travel_countries=_split_setting(
            settings.user_travel_countries
        ),
        travel_destination=settings.user_travel_destination,
        travel_preferences=_split_setting(
            settings.user_travel_preferences
        ),
        travel_interests=_split_setting(
            settings.user_travel_interests
        ),
        lifestyle=_split_setting(settings.user_lifestyle),
        personality=_split_setting(settings.user_personality),
        dating_preferences=_split_setting(
            settings.user_dating_preferences
        ),
        communication_style=_split_setting(
            settings.user_communication_style
        ),
        relationship_goals=_split_setting(
            settings.user_relationship_goals
        ),
        additional_context=settings.user_additional_context,
    )
