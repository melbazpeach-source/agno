"""
BUG #3980 regression guard: store_history_messages default.

When store_history_messages=True (the old default), each run stored ALL
messages including history from prior runs, causing O(N^2) storage growth
and ~150x token inflation. Fixed by changing default to False.
"""
from agno.agent.agent import Agent


def test_store_history_messages_defaults_to_false():
    """
    BUG #3980: store_history_messages was True, causing quadratic storage
    growth. With 20 runs, users hit 5M+ tokens (expected ~34K).
    """
    agent = Agent()
    assert agent.store_history_messages is False, (
        "store_history_messages should default to False to prevent O(N^2) "
        "token inflation (Bug #3980)"
    )
