"""
BUG #3968 repro: Bedrock model not properly refreshing AWS token.

The AwsBedrockClaude model extracts AWS credentials as raw strings from a
boto3 Session ONCE, then caches the client forever. When short-lived
credentials expire (~1 hour for IAM roles), all subsequent calls fail.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from agno.models.aws.claude import Claude


def _fake_creds(suffix: str):
    return SimpleNamespace(
        access_key=f"AKIA-{suffix}",
        secret_key=f"SECRET-{suffix}",
        token=f"TOKEN-{suffix}",
    )


def test_get_async_client_recreates_closed_cached_client():
    """
    BUG #3968(a): get_async_client() should check is_closed() and recreate
    a closed/expired client. Current code (line 131) only checks
    `if self.async_client is not None` — no is_closed() check.
    """
    model = Claude(api_key="test-key", aws_region="us-east-1")

    closed_async_client = MagicMock()
    closed_async_client.is_closed.return_value = True
    model.async_client = closed_async_client

    with (
        patch.object(model, "_get_client_params", return_value={"api_key": "test-key", "aws_region": "us-east-1"}),
        patch("agno.models.aws.claude.get_default_async_client", return_value=MagicMock()),
        patch("agno.models.aws.claude.AsyncAnthropicBedrock") as mock_async_ctor,
    ):
        replacement_client = MagicMock()
        mock_async_ctor.return_value = replacement_client

        client = model.get_async_client()

    # FAILS on current code: is_closed() is never called on the async client
    closed_async_client.is_closed.assert_called_once()
    assert client is replacement_client


def test_get_client_should_refresh_rotating_session_credentials():
    """
    BUG #3968(b): When using a boto3 Session with short-lived credentials,
    get_client() caches the first client forever and never re-calls
    _get_client_params() to pick up refreshed credentials.

    _get_client_params() itself correctly calls session.get_credentials()
    each time, but get_client() bypasses it via the cached client.
    """
    session = MagicMock()
    session.region_name = "us-west-2"
    session.get_credentials.side_effect = [
        _fake_creds("1"),
        _fake_creds("2"),
        _fake_creds("3"),
        _fake_creds("4"),
    ]

    model = Claude(session=session)

    # Part (b): _get_client_params() reads fresh credentials each call
    first = model._get_client_params()
    second = model._get_client_params()
    assert first["aws_access_key"] == "AKIA-1"
    assert second["aws_access_key"] == "AKIA-2"

    with (
        patch("agno.models.aws.claude.get_default_sync_client", return_value=MagicMock()),
        patch("agno.models.aws.claude.AnthropicBedrock") as mock_ctor,
    ):
        first_client = MagicMock()
        first_client.is_closed.return_value = False
        second_client = MagicMock()
        second_client.is_closed.return_value = False
        mock_ctor.side_effect = [first_client, second_client]

        client_one = model.get_client()
        client_two = model.get_client()

    # FAILS on current code: second get_client() returns cached client,
    # never calling _get_client_params() with fresh credentials (AKIA-3/4).
    assert session.get_credentials.call_count == 4
    assert client_one is first_client
    assert client_two is second_client
