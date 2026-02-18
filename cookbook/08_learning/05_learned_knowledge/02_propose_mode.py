"""
Learned Knowledge: Propose Mode (Deep Dive)
===========================================
Agent proposes learnings, then HITL confirmation gates save_learning.

PROPOSE mode adds human quality control:
1. Agent identifies valuable insights
2. Agent proposes them in its response
3. Agent calls save_learning (requires confirmation)
4. System pauses for user confirmation before execution

Use when quality matters more than speed.

Compare with: 01_agentic_mode.py for automatic saving.
See also: 01_basics/4_learned_knowledge.py for the basics.
"""

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.learn import LearnedKnowledgeConfig, LearningMachine, LearningMode
from agno.models.openai import OpenAIResponses
from agno.utils import pprint
from agno.vectordb.pgvector import PgVector, SearchType

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
db = PostgresDb(db_url=db_url)

knowledge = Knowledge(
    vector_db=PgVector(
        db_url=db_url,
        table_name="propose_learnings",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)

agent = Agent(
    model=OpenAIResponses(id="gpt-5.2"),
    db=db,
    instructions=(
        "When you discover a valuable insight, include a Proposed Learning block and then call save_learning. "
        "Do not ask for a second yes/no in chat; the system handles confirmation."
    ),
    learning=LearningMachine(
        knowledge=knowledge,
        learned_knowledge=LearnedKnowledgeConfig(
            mode=LearningMode.PROPOSE,
        ),
    ),
    markdown=True,
)


def run_with_hitl_confirmation(
    message: str, user_id: str, session_id: str, approve: bool
):
    """Run the agent and handle HITL confirmation for save_learning.

    In PROPOSE mode, save_learning requires confirmation. When the agent calls it,
    the run pauses and returns active_requirements. We confirm or reject, then
    continue the run.

    In AgentOS/AgUI, this confirmation is handled automatically by the frontend UI.
    """
    run_response = agent.run(
        message,
        user_id=user_id,
        session_id=session_id,
    )
    pprint.pprint_run_response(run_response)

    while run_response.is_paused:
        resolved_confirmation = False
        for requirement in run_response.active_requirements:
            if requirement.needs_confirmation:
                resolved_confirmation = True
                if approve:
                    print("  -> Confirming save_learning")
                    requirement.confirm()
                else:
                    print("  -> Rejecting save_learning")
                    requirement.reject(note="Rejected by user in PROPOSE mode demo.")

        if not resolved_confirmation:
            break

        run_response = agent.continue_run(
            run_id=run_response.run_id,
            requirements=run_response.requirements,
        )
        pprint.pprint_run_response(run_response)

    return run_response


# ---------------------------------------------------------------------------
# Run Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    user_id = "propose@example.com"
    session_id = "propose_session"

    # Approval example
    print("\n" + "=" * 60)
    print("MESSAGE 1: User shares experience (approve)")
    print("=" * 60 + "\n")

    run_with_hitl_confirmation(
        message=(
            "I just spent 2 hours debugging why my Docker container couldn't "
            "connect to localhost. Turns out you need to use host.docker.internal "
            "on Mac to access the host machine from inside a container."
        ),
        user_id=user_id,
        session_id=session_id,
        approve=True,
    )
    agent.learning_machine.learned_knowledge_store.print(query="docker localhost")

    # Rejection example
    print("\n" + "=" * 60)
    print("MESSAGE 2: User shares, then rejects")
    print("=" * 60 + "\n")

    run_with_hitl_confirmation(
        message="I fixed my bug by restarting my computer.",
        user_id=user_id,
        session_id="session_2",
        approve=False,
    )
    agent.learning_machine.learned_knowledge_store.print(query="restart")
