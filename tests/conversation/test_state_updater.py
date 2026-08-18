
from app.conversation.analyzer import MessageAnalyzer
from app.conversation.state import ConversationState
from app.conversation.enums import ConversationStage
from app.conversation.state_updater import ConversationStateUpdater


def test_interest_signal_updates_interest():
    analyzer = MessageAnalyzer()
    updater = ConversationStateUpdater()
    state = ConversationState()

    analysis = analyzer.analyze("Ты мне очень нравишься")
    state = updater.update(state, analysis)

    assert state.interest_score > 0.0


def test_mutuality_signal_updates_mutuality():
    analyzer = MessageAnalyzer()
    updater = ConversationStateUpdater()
    state = ConversationState()

    analysis = analyzer.analyze("Я тоже хочу тебя увидеть")
    state = updater.update(state, analysis)

    assert state.mutuality_score > 0.0


def test_comfort_signal_updates_comfort():
    analyzer = MessageAnalyzer()
    updater = ConversationStateUpdater()
    state = ConversationState()

    analysis = analyzer.analyze("Мне очень комфортно с тобой")
    state = updater.update(state, analysis)

    assert state.comfort_score > 0.0


def test_flirt_signal_updates_flirt():
    analyzer = MessageAnalyzer()
    updater = ConversationStateUpdater()
    state = ConversationState()

    analysis = analyzer.analyze("Ты очень привлекательный мужчина")
    state = updater.update(state, analysis)

    assert state.flirt_score > 0.0


def test_meeting_signal_updates_meeting_readiness():
    analyzer = MessageAnalyzer()
    updater = ConversationStateUpdater()
    state = ConversationState()

    analysis = analyzer.analyze("Давай встретимся завтра")
    state = updater.update(state, analysis)

    assert state.meeting_readiness > 0.0


def test_positive_chat_without_meeting_signal_does_not_trigger_meeting():
    analyzer = MessageAnalyzer()
    updater = ConversationStateUpdater()
    state = ConversationState()

    messages = [
        "Мне интересно с тобой",
        "Мне очень комфортно с тобой",
        "Ты очень привлекательный мужчина",
        "Я тоже думаю, что ты классный",
    ]

    for text in messages:
        analysis = analyzer.analyze(text)
        state = updater.update(state, analysis)

    assert state.meeting_readiness < 0.75
    assert state.stage != ConversationStage.MEETING


def test_explicit_meeting_signal_can_trigger_meeting():
    analyzer = MessageAnalyzer()
    updater = ConversationStateUpdater()
    state = ConversationState()

    messages = [
        "Мне интересно с тобой",
        "Мне очень комфортно с тобой",
        "Ты очень привлекательный мужчина",
        "Давай встретимся завтра",
    ]

    for text in messages:
        analysis = analyzer.analyze(text)
        state = updater.update(state, analysis)

    assert state.meeting_readiness >= 0.75
    assert state.stage == ConversationStage.MEETING
