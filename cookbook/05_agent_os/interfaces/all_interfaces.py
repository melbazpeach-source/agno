"""
AgentOS Cookbook for generating OpenAPI documentation for docs
"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.os.interfaces.a2a import A2A
from agno.os.interfaces.agui import AGUI
from agno.os.interfaces.slack import Slack
from agno.os.interfaces.whatsapp import Whatsapp
from agno.registry import Registry
from agno.tools.mcp import MCPTools

# --- Setup ---

db = SqliteDb(id="docs-os-demo", db_file="tmp/docs.db")

agent = Agent(
    name="Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=["You are an expert in the Agno framework."],
    db=db,
)
registry = Registry(
    name="Agno Registry",
    tools=[MCPTools(transport="streamable-http", url="https://docs.agno.com/mcp")],
    models=[
        OpenAIChat(id="gpt-4o-mini"),
    ],
    dbs=[db],
)


# # Create an interface
slack_interface = Slack(agent=agent)
whatsapp_interface = Whatsapp(agent=agent)
agui_interface = AGUI(agent=agent)
a2a_interface = A2A(agents=[agent])

agent_os = AgentOS(
    name="Documentation all API references",
    agents=[agent],
    registry=registry,
    db=db,
    interfaces=[slack_interface, whatsapp_interface, agui_interface, a2a_interface],
)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="all_interfaces:app", reload=True)
