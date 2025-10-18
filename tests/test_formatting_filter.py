import pytest

from src.message_renderer import SlackMessageHtmlRenderer


@pytest.fixture
def renderer():
    return SlackMessageHtmlRenderer()


def test_formatting_filter_handles_bold_and_italic(renderer):
    text = "Mixing *italic* and **bold** plus __alt bold__ and _alt italic_."

    formatted = renderer._formatting_filter(text)

    assert "<em>italic</em>" in formatted
    assert "<strong>bold</strong>" in formatted
    assert "<strong>alt bold</strong>" in formatted
    assert "<em>alt italic</em>" in formatted


def test_formatting_filter_respects_escaped_markers(renderer):
    text = r"\*escaped\* and **styled**"

    formatted = renderer._formatting_filter(text)

    assert "*escaped*" in formatted
    assert "<strong>styled</strong>" in formatted
