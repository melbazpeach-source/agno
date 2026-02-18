"""
BUG #4430 repro: Bedrock structured output uses toolChoice: auto instead of
forcing the specific tool.

When using output_schema with Bedrock models, the tool_choice parameter is
accepted by invoke() but never wired into the toolConfig sent to the API.
This means the model can choose to ignore the structured output tool.
"""
from unittest.mock import MagicMock, patch

from agno.models.aws.bedrock import AwsBedrock


def test_invoke_passes_tool_choice_to_bedrock_api():
    """
    BUG #4430 repro:
    invoke() receives tool_choice but never includes it in the toolConfig
    sent to the Bedrock Converse API. Lines 456-458 build toolConfig with
    only "tools" — no "toolChoice" key.
    """
    model = AwsBedrock(id="us.amazon.nova-pro-v1:0", aws_region="us-east-1")

    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {"message": {"role": "assistant", "content": [{"text": '{"answer": "test"}'}]}},
        "usage": {"inputTokens": 10, "outputTokens": 5, "totalTokens": 15},
        "stopReason": "end_turn",
    }

    tools = [
        {
            "type": "function",
            "function": {
                "name": "MyOutputModel",
                "description": "structured output schema",
                "parameters": {
                    "type": "object",
                    "properties": {"answer": {"type": "string"}},
                    "required": ["answer"],
                },
            },
        }
    ]

    with patch.object(model, "get_client", return_value=mock_client):
        with patch.object(model, "_format_messages", return_value=([], None)):
            model.invoke(
                messages=[],
                assistant_message=MagicMock(),
                tools=tools,
                tool_choice={"tool": {"name": "MyOutputModel"}},
            )

    call_kwargs = mock_client.converse.call_args
    tool_config = call_kwargs.kwargs.get("toolConfig") or call_kwargs[1].get("toolConfig")

    assert tool_config is not None, "toolConfig should be present"
    assert "tools" in tool_config
    # FAILS on current code: toolChoice is never included
    assert "toolChoice" in tool_config, (
        f"toolChoice should be in toolConfig but got: {tool_config}"
    )
