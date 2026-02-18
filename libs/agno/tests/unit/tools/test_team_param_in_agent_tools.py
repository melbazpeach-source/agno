"""
BUG #4724: Team parameter not passed to tool functions on member agents.

When a Toolkit tool declares a `team` parameter and is registered on an Agent
that is a member of a Team, the tool receives `None` instead of the Team object.

Root cause: `agent/_tools.py` sets `_func._agent = agent` but never sets
`_func._team`.  The Team reference is only propagated for tools registered
directly on the Team (in `team/_tools.py`), not for tools on member agents.
"""
import ast
import inspect

import agno.agent._tools as agent_tools_module
import agno.team._tools as team_tools_module


def test_agent_tools_module_sets_team():
    """
    BUG #4724: agent/_tools.py never sets _func._team on tool functions.

    Compare agent/_tools.py (parse_tools) with team/_tools.py (parse_tools):
    - team/_tools.py sets _func._team = team  -> correct
    - agent/_tools.py only sets _func._agent = agent -> _team stays None

    This AST test checks whether agent/_tools.py has any assignment to _team.
    """
    source = inspect.getsource(agent_tools_module)
    tree = ast.parse(source)

    # Find the parse_tools function in agent/_tools.py
    found_parse_tools = False
    sets_team = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "parse_tools":
            found_parse_tools = True
            # Check if _team is assigned anywhere in parse_tools
            for child in ast.walk(node):
                if isinstance(child, ast.Attribute):
                    if child.attr == "_team" and isinstance(child.ctx, ast.Store):
                        sets_team = True
            break

    assert found_parse_tools, "Could not find parse_tools in agent/_tools.py"

    # BUG: agent/_tools.py does NOT set _team on functions
    assert sets_team, (
        "BUG #4724: agent/_tools.py:parse_tools does not set _func._team. "
        "When a tool declares a `team` parameter, it receives None instead "
        "of the Team object. Compare with team/_tools.py which does set _team."
    )


def test_team_tools_module_sets_team():
    """
    Sanity check: team/_tools.py DOES set _func._team correctly.
    The function is _determine_tools_for_model (not parse_tools like agent).
    """
    source = inspect.getsource(team_tools_module)
    tree = ast.parse(source)

    found_func = False
    sets_team = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_determine_tools_for_model":
            found_func = True
            for child in ast.walk(node):
                if isinstance(child, ast.Attribute):
                    if child.attr == "_team" and isinstance(child.ctx, ast.Store):
                        sets_team = True
            break

    assert found_func, "Could not find _determine_tools_for_model in team/_tools.py"
    assert sets_team, "team/_tools.py should set _func._team (this is the working path)"
