from app.ai.prompts import SYSTEM_PROMPT


def test_prompt_requires_natural_dialogue():
    assert "Не воспринимай разговор как серию вопросов и ответов." in SYSTEM_PROMPT
    assert "Не задавай вопрос только потому" in SYSTEM_PROMPT


def test_prompt_allows_answer_without_question():
    assert "Сообщение не обязано содержать вопрос." in SYSTEM_PROMPT


def test_prompt_requires_tu_form():
    assert "Всегда обращайся к собеседнице на «ты»." in SYSTEM_PROMPT
    assert "Никогда не используй «вы»." in SYSTEM_PROMPT


def test_prompt_prevents_interview_style():
    assert "Не превращай переписку в интервью." in SYSTEM_PROMPT
    assert "Не задавай несколько вопросов подряд." in SYSTEM_PROMPT


def test_prompt_prevents_fabrication():
    assert "Не выдумывай:" in SYSTEM_PROMPT
    assert "Если нужной информации нет, не придумывай её." in SYSTEM_PROMPT
