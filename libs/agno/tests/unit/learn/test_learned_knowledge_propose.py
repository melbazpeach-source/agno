import inspect

import pytest

from agno.learn.config import LearnedKnowledgeConfig, LearningMode
from agno.learn.stores.learned_knowledge import LearnedKnowledgeStore
from agno.tools.function import Function


def _make_store(mode: LearningMode) -> LearnedKnowledgeStore:
    return LearnedKnowledgeStore(config=LearnedKnowledgeConfig(mode=mode))


def test_propose_mode_save_tool_has_requires_confirmation():
    store = _make_store(LearningMode.PROPOSE)

    tools = store.get_agent_tools(
        user_id="user_1",
        agent_id="agent_1",
        team_id="team_1",
        namespace="global",
    )

    save_tools = [t for t in tools if isinstance(t, Function) and t.name == "save_learning"]
    assert len(save_tools) == 1
    assert save_tools[0].requires_confirmation is True


def test_propose_mode_search_tool_no_confirmation():
    store = _make_store(LearningMode.PROPOSE)

    tools = store.get_agent_tools(
        user_id="user_1",
        agent_id="agent_1",
        namespace="global",
    )

    search_tools = [t for t in tools if callable(t) and getattr(t, "__name__", "") == "search_learnings"]
    assert len(search_tools) == 1
    # search_learnings should not be wrapped in Function with confirmation
    assert not isinstance(search_tools[0], Function)


def test_agentic_mode_save_tool_is_bare_callable():
    store = _make_store(LearningMode.AGENTIC)

    tools = store.get_agent_tools(
        user_id="user_1",
        agent_id="agent_1",
        namespace="global",
    )

    # In AGENTIC mode, save_learning should be a bare callable, not a Function
    assert any(callable(t) and getattr(t, "__name__", "") == "save_learning" for t in tools)
    assert not any(isinstance(t, Function) and t.name == "save_learning" for t in tools)


@pytest.mark.asyncio
async def test_propose_mode_async_save_tool_has_requires_confirmation():
    store = _make_store(LearningMode.PROPOSE)

    tools = await store.aget_agent_tools(
        user_id="user_1",
        agent_id="agent_1",
        team_id="team_1",
        namespace="global",
    )

    save_tools = [t for t in tools if isinstance(t, Function) and t.name == "save_learning"]
    assert len(save_tools) == 1
    assert save_tools[0].requires_confirmation is True
    assert inspect.iscoroutinefunction(save_tools[0].entrypoint)


def test_propose_mode_context_uses_hitl_not_chat_yes_no():
    store = _make_store(LearningMode.PROPOSE)

    context = store._build_propose_mode_context(data=None)

    assert "**RULE 3: After proposing, call `save_learning` immediately.**" in context
    assert "The system handles user confirmation via HITL" in context
    assert 'Do NOT ask for a separate "yes/no" confirmation in chat.' in context
    # Old conversational confirmation patterns should NOT be present
    assert 'Call `save_learning` ONLY after the user says "yes" to your proposal.' not in context
    assert "Save this to the knowledge base? (yes/no)" not in context


def test_propose_mode_no_save_instructions_when_agent_can_save_false():
    store = LearnedKnowledgeStore(config=LearnedKnowledgeConfig(mode=LearningMode.PROPOSE, agent_can_save=False))

    tools = store.get_agent_tools(user_id="u1", agent_id="a1", namespace="global")
    # Only search tool should be present
    assert len(tools) == 1
    assert getattr(tools[0], "__name__", "") == "search_learnings"

    context = store._build_propose_mode_context(data=None)
    # Prompt should NOT mention save_learning when tool isn't exposed
    assert "save_learning" not in context
    assert "RULE 3" not in context
