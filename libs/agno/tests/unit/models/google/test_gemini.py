from unittest.mock import MagicMock, patch

from pydantic import BaseModel

from agno.models.google.gemini import Gemini


def test_gemini_get_client_with_credentials_vertexai():
    """Test that credentials are correctly passed to the client when vertexai is True."""
    mock_credentials = MagicMock()
    model = Gemini(vertexai=True, project_id="test-project", location="test-location", credentials=mock_credentials)

    with patch("agno.models.google.gemini.genai.Client") as mock_client_cls:
        model.get_client()

        # Verify credentials were passed to the client
        _, kwargs = mock_client_cls.call_args
        assert kwargs["credentials"] == mock_credentials
        assert kwargs["vertexai"] is True
        assert kwargs["project"] == "test-project"
        assert kwargs["location"] == "test-location"


def test_gemini_get_client_without_credentials_vertexai():
    """Test that client is initialized without credentials when not provided in vertexai mode."""
    model = Gemini(vertexai=True, project_id="test-project", location="test-location")

    with patch("agno.models.google.gemini.genai.Client") as mock_client_cls:
        model.get_client()

        # Verify credentials were NOT passed to the client
        _, kwargs = mock_client_cls.call_args
        assert "credentials" not in kwargs
        assert kwargs["vertexai"] is True


def test_gemini_get_client_ai_studio_mode():
    """Test that credentials are NOT passed in Google AI Studio mode (non-vertexai)."""
    mock_credentials = MagicMock()
    # Even if credentials are provided, they shouldn't be passed if vertexai=False
    model = Gemini(vertexai=False, api_key="test-api-key", credentials=mock_credentials)

    with patch("agno.models.google.gemini.genai.Client") as mock_client_cls:
        model.get_client()

        # Verify credentials were NOT passed to the client
        _, kwargs = mock_client_cls.call_args
        assert "credentials" not in kwargs
        assert "api_key" in kwargs
        assert kwargs.get("vertexai") is not True


# ---------------------------------------------------------------------------
# BUG #3964 repro: response_mime_type + tools conflict
# ---------------------------------------------------------------------------


class _GeminiStructuredResponse(BaseModel):
    answer: str


def test_get_request_params_omits_response_mime_type_when_tools_present():
    """
    BUG #3964 repro:
    When tools are present, response_mime_type should NOT be set because
    the Gemini API rejects combining response_mime_type with function calling.

    Current code at gemini.py:274 unconditionally sets response_mime_type
    for any Pydantic response_format, even when tools are also present.
    """
    model = Gemini(api_key="test-api-key")
    tools = [
        {
            "type": "function",
            "function": {
                "name": "lookup_weather",
                "description": "Get weather by city",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            },
        }
    ]

    request_params = model.get_request_params(response_format=_GeminiStructuredResponse, tools=tools)
    config = request_params["config"].model_dump(exclude_none=True)

    assert "tools" in config
    assert "response_schema" in config
    # This FAILS on current code: response_mime_type is always set for Pydantic response_format
    assert "response_mime_type" not in config


# ---------------------------------------------------------------------------
# BUG #4298 repro: cached_content + tools/system_instruction conflict
# ---------------------------------------------------------------------------


def test_get_request_params_strips_conflicting_keys_when_cached_content_present():
    """
    BUG #4298 repro:
    When cached_content is set, the Gemini API rejects requests that also
    include system_instruction, tools, or tool_config — those are already
    baked into the cache.

    Current code at gemini.py:266 sets cached_content, but lines 271,
    327-332, and 334-344 unconditionally add system_instruction, tools,
    and tool_config alongside it.
    """
    model = Gemini(api_key="test-api-key", cached_content="caches/abc123")
    tools = [
        {
            "type": "function",
            "function": {
                "name": "lookup_weather",
                "description": "Get weather by city",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            },
        }
    ]

    request_params = model.get_request_params(
        system_message="You are a helpful assistant.",
        tools=tools,
        tool_choice="auto",
    )
    config = request_params["config"].model_dump(exclude_none=True)

    assert "cached_content" in config
    # These FAIL on current code: all three are included alongside cached_content
    assert "system_instruction" not in config
    assert "tools" not in config
    assert "tool_config" not in config
