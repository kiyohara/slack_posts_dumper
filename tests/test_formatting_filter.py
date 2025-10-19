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


def test_formatting_filter_requires_whitespace_boundaries(renderer):
    text = "word1*word2*word3 word1 *word2*word3 word1*word2* word3 word1 *word2* word3"

    formatted = renderer._formatting_filter(text)

    assert "word1*word2*word3" in formatted
    assert "word1 *word2*word3" in formatted
    assert "word1*word2* word3" in formatted
    assert "word1 <strong>word2</strong> word3" in formatted


def test_formatting_filter_handles_strikethrough_and_combo(renderer):
    text = "Use ~deprecated~ APIs and _*very important*_ notices."

    formatted = renderer._formatting_filter(text)

    assert "<del>deprecated</del>" in formatted
    assert "<em><strong>very important</strong></em>" in formatted


def test_formatting_filter_accepts_punctuation_boundaries(renderer):
    text = "Punct (*bold*) keeps emphasis and closing *word*."

    formatted = renderer._formatting_filter(text)

    assert "(<strong>bold</strong>)" in formatted
    assert "<strong>word</strong>." in formatted


def test_formatting_filter_ignores_markers_inside_code(renderer):
    text = "`*code bold*` and ```\n_some code_\n``` stay literal, but *bold* converts."

    formatted = renderer._formatting_filter(text)

    assert "`*code bold*`" in formatted
    assert "```\n_some code_\n```" in formatted
    assert "<strong>bold</strong>" in formatted


def test_render_pipeline_preserves_links_after_markup(renderer):
    class DummyUserResolver:
        def get_user_info(self, user_id):
            return {
                "profile": {"image_72": "https://example.com/avatar.png"},
                "display_name": "Tester",
            }

        def get_user_display_name(self, user_id, force_refresh: bool = False):
            return "Tester"

    message = {
        "user": "U123",
        "ts": "1710000000.0",
        "text": "<@U123> check _updates_ at <http://example.com/some_path>.",
    }

    html = renderer.render(message, user_resolver=DummyUserResolver())

    assert "@Tester" in html
    assert "<em>updates</em>" in html
    assert 'href="http://example.com/some_path"' in html
    assert 'target="_blank"' in html
    assert "<em>http://example.com/some_path</em>" not in html
