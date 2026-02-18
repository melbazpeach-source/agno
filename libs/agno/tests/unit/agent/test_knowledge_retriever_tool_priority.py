"""Tests that knowledge_retriever takes priority over knowledge when registering search tools.

Regression test for https://github.com/agno-agi/agno/issues/6533
The v2.5 refactor introduced a bug where the search_knowledge tool would use
Knowledge.get_tools() (which calls the vector DB directly) instead of the
custom knowledge_retriever, when both were set on an Agent.
"""

import pytest

from agno.agent import Agent
from agno.agent._tools import aget_tools, get_tools
from agno.models.base import Function
from agno.run.agent import RunOutput
from agno.run.base import RunContext
from agno.session.agent import AgentSession


class MockKnowledge:
    """Minimal mock that satisfies the knowledge protocol."""

    def __init__(self):
        self.max_results = 5
        self.vector_db = None

    def get_tools(self, **kwargs):
        return [Function(name="search_knowledge_base_from_knowledge", entrypoint=lambda query: "from knowledge")]

    async def aget_tools(self, **kwargs):
        return [Function(name="search_knowledge_base_from_knowledge", entrypoint=lambda query: "from knowledge")]


def _make_run_context():
    return RunContext(run_id="test-run", session_id="test-session")


def _make_session():
    return AgentSession(session_id="test-session")


def _make_run_response():
    return RunOutput(run_id="test-run", session_id="test-session", agent_id="test-agent")


def test_get_tools_uses_retriever_when_both_knowledge_and_retriever_set():
    """When both knowledge and knowledge_retriever are set, get_tools should use the retriever."""

    def custom_retriever(query, agent=None, num_documents=None, **kwargs):
        return [{"content": "from retriever"}]

    agent = Agent()
    agent.knowledge = MockKnowledge()  # type: ignore
    agent.knowledge_retriever = custom_retriever  # type: ignore
    agent.search_knowledge = True

    tools = get_tools(agent, _make_run_response(), _make_run_context(), _make_session())

    # Find the knowledge search tool
    knowledge_tools = [t for t in tools if isinstance(t, Function) and "knowledge" in t.name.lower()]
    assert len(knowledge_tools) == 1
    # Should be the retriever-based tool, not the Knowledge.get_tools() one
    assert knowledge_tools[0].name == "search_knowledge_base"


def test_get_tools_uses_knowledge_when_only_knowledge_set():
    """When only knowledge is set (no retriever), get_tools should use Knowledge.get_tools()."""

    agent = Agent()
    agent.knowledge = MockKnowledge()  # type: ignore
    agent.knowledge_retriever = None
    agent.search_knowledge = True

    tools = get_tools(agent, _make_run_response(), _make_run_context(), _make_session())

    knowledge_tools = [t for t in tools if isinstance(t, Function) and "knowledge" in t.name.lower()]
    assert len(knowledge_tools) == 1
    assert knowledge_tools[0].name == "search_knowledge_base_from_knowledge"


def test_get_tools_uses_retriever_when_only_retriever_set():
    """When only knowledge_retriever is set (no knowledge), get_tools should use the retriever."""

    def custom_retriever(query, agent=None, num_documents=None, **kwargs):
        return [{"content": "from retriever"}]

    agent = Agent()
    agent.knowledge = None
    agent.knowledge_retriever = custom_retriever  # type: ignore
    agent.search_knowledge = True

    tools = get_tools(agent, _make_run_response(), _make_run_context(), _make_session())

    knowledge_tools = [t for t in tools if isinstance(t, Function) and "knowledge" in t.name.lower()]
    assert len(knowledge_tools) == 1
    assert knowledge_tools[0].name == "search_knowledge_base"


@pytest.mark.asyncio
async def test_aget_tools_uses_retriever_when_both_knowledge_and_retriever_set():
    """Async variant: when both are set, aget_tools should use the retriever."""

    def custom_retriever(query, agent=None, num_documents=None, **kwargs):
        return [{"content": "from retriever"}]

    agent = Agent()
    agent.knowledge = MockKnowledge()  # type: ignore
    agent.knowledge_retriever = custom_retriever  # type: ignore
    agent.search_knowledge = True

    tools = await aget_tools(agent, _make_run_response(), _make_run_context(), _make_session())

    knowledge_tools = [t for t in tools if isinstance(t, Function) and "knowledge" in t.name.lower()]
    assert len(knowledge_tools) == 1
    assert knowledge_tools[0].name == "search_knowledge_base"


@pytest.mark.asyncio
async def test_aget_tools_uses_knowledge_when_only_knowledge_set():
    """Async variant: when only knowledge is set, aget_tools should use Knowledge.aget_tools()."""

    agent = Agent()
    agent.knowledge = MockKnowledge()  # type: ignore
    agent.knowledge_retriever = None
    agent.search_knowledge = True

    tools = await aget_tools(agent, _make_run_response(), _make_run_context(), _make_session())

    knowledge_tools = [t for t in tools if isinstance(t, Function) and "knowledge" in t.name.lower()]
    assert len(knowledge_tools) == 1
    assert knowledge_tools[0].name == "search_knowledge_base_from_knowledge"
