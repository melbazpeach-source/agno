"""Tests that knowledge_retriever takes priority over knowledge when registering search tools on Team.

Regression test for https://github.com/agno-agi/agno/issues/6533
Same bug as Agent: when both knowledge and knowledge_retriever are set,
the tool registration ignores the custom retriever.
"""

from unittest.mock import MagicMock

from agno.models.base import Function
from agno.run.base import RunContext
from agno.run.team import TeamRunOutput
from agno.session.team import TeamSession
from agno.team.team import Team


class MockKnowledge:
    """Minimal mock that satisfies the knowledge protocol."""

    def __init__(self):
        self.max_results = 5
        self.vector_db = None

    def get_tools(self, **kwargs):
        return [Function(name="search_knowledge_base_from_knowledge", entrypoint=lambda query: "from knowledge")]


def _make_run_context():
    return RunContext(run_id="test-run", session_id="test-session")


def _make_session():
    return TeamSession(session_id="test-session")


def _make_run_response():
    return TeamRunOutput(run_id="test-run", session_id="test-session", team_id="test-team")


def _make_model():
    model = MagicMock()
    model.get_tools_for_api.return_value = []
    model.add_tool.return_value = None
    return model


def _get_knowledge_tools(tools):
    """Extract knowledge-related tools from the tool list."""
    return [t for t in tools if isinstance(t, Function) and "knowledge" in t.name.lower()]


def test_team_tools_use_retriever_when_both_knowledge_and_retriever_set():
    """When both knowledge and knowledge_retriever are set, tool registration should use the retriever."""
    from agno.team._tools import _determine_tools_for_model

    def custom_retriever(query, team=None, num_documents=None, **kwargs):
        return [{"content": "from retriever"}]

    team = Team(name="test-team", members=[])
    team.knowledge = MockKnowledge()  # type: ignore
    team.knowledge_retriever = custom_retriever  # type: ignore
    team.search_knowledge = True

    tools = _determine_tools_for_model(
        team=team,
        model=_make_model(),
        run_response=_make_run_response(),
        run_context=_make_run_context(),
        team_run_context={},
        session=_make_session(),
        async_mode=False,
    )

    knowledge_tools = _get_knowledge_tools(tools)
    assert len(knowledge_tools) == 1
    assert knowledge_tools[0].name == "search_knowledge_base"


def test_team_tools_use_knowledge_when_only_knowledge_set():
    """When only knowledge is set (no retriever), tool registration should use Knowledge.get_tools()."""
    from agno.team._tools import _determine_tools_for_model

    team = Team(name="test-team", members=[])
    team.knowledge = MockKnowledge()  # type: ignore
    team.knowledge_retriever = None
    team.search_knowledge = True

    tools = _determine_tools_for_model(
        team=team,
        model=_make_model(),
        run_response=_make_run_response(),
        run_context=_make_run_context(),
        team_run_context={},
        session=_make_session(),
        async_mode=False,
    )

    knowledge_tools = _get_knowledge_tools(tools)
    assert len(knowledge_tools) == 1
    assert knowledge_tools[0].name == "search_knowledge_base_from_knowledge"


def test_team_tools_use_retriever_when_only_retriever_set():
    """When only knowledge_retriever is set (no knowledge), tool registration should use the retriever."""
    from agno.team._tools import _determine_tools_for_model

    def custom_retriever(query, team=None, num_documents=None, **kwargs):
        return [{"content": "from retriever"}]

    team = Team(name="test-team", members=[])
    team.knowledge = None
    team.knowledge_retriever = custom_retriever  # type: ignore
    team.search_knowledge = True

    tools = _determine_tools_for_model(
        team=team,
        model=_make_model(),
        run_response=_make_run_response(),
        run_context=_make_run_context(),
        team_run_context={},
        session=_make_session(),
        async_mode=False,
    )

    knowledge_tools = _get_knowledge_tools(tools)
    assert len(knowledge_tools) == 1
    assert knowledge_tools[0].name == "search_knowledge_base"
