"""
BUG #4184 repro: Cross-provider session incompatibility.

When a session stores tool result messages from Gemini (list format) and
they are later replayed through OpenAI, the content format is incompatible.
OpenAI expects tool message content to be a string, but Gemini stores it
as a list of dicts.
"""
from agno.models.message import Message
from agno.models.openai.chat import OpenAIChat


def test_openai_format_message_normalizes_tool_list_content_to_string():
    """
    BUG #4184: Gemini-style tool content is list[dict], but OpenAI
    tool messages require string content. OpenAIChat._format_message
    currently passes list content through unchanged, causing a 400 error.
    """
    model = OpenAIChat(id="gpt-4o-mini", api_key="test-key")

    # Simulate a tool result message stored by Gemini (list format)
    gemini_tool_message = Message(
        role="tool",
        tool_call_id="call_123",
        content=[{"text": "tool result from gemini"}],
    )

    formatted = model._format_message(gemini_tool_message)

    # FAILS on current code: content remains a list instead of being
    # normalized to string for OpenAI compatibility
    assert isinstance(formatted["content"], str)
    assert formatted["content"] == gemini_tool_message.get_content_string()
