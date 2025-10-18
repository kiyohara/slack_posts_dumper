import pytest

from src.message_renderer import SlackMessageHtmlRenderer


@pytest.fixture
def renderer():
    return SlackMessageHtmlRenderer()


def test_formatting_filter_handles_bold_and_italic(renderer):
    text = "Mixing *bold* and **extra bold** plus __alt bold__ and _alt italic_."

    formatted = renderer._formatting_filter(text)

    assert "<strong>bold</strong>" in formatted
    assert "<strong>extra bold</strong>" in formatted
    assert "<strong>alt bold</strong>" in formatted
    assert "<em>alt italic</em>" in formatted


def test_formatting_filter_respects_escaped_markers(renderer):
    text = r"\*escaped\* and **styled**"

    formatted = renderer._formatting_filter(text)

    assert "*escaped*" in formatted
    assert "<strong>styled</strong>" in formatted


def test_formatting_filter_skips_markers_inside_words(renderer):
    text = "Keep variable_name and mid*word untouched while _italic_ works."

    formatted = renderer._formatting_filter(text)

    assert "variable_name" in formatted
    assert "mid*word" in formatted
    assert "<em>italic</em>" in formatted


def test_formatting_filter_handles_strikethrough_and_combo(renderer):
    text = "Use ~deprecated~ APIs and _*very important*_ notices."

    formatted = renderer._formatting_filter(text)

    assert "<del>deprecated</del>" in formatted
    assert "<em><strong>very important</strong></em>" in formatted


def test_formatting_filter_ignores_markers_inside_code(renderer):
    text = "`*code bold*` and ```\n_some code_\n``` stay literal, but *bold* converts."

    formatted = renderer._formatting_filter(text)

    assert "`*code bold*`" in formatted
    assert "```\n_some code_\n```" in formatted
    assert "<strong>bold</strong>" in formatted
