# human_in_the_loop

Examples for confirmation flows, user input prompts, and session state persistence during HITL pauses.

## Files
- `confirmation_with_session_state.py` - Confirmation flow where the tool modifies session_state before pausing. Verifies that state changes survive the pause/continue round-trip.

## Prerequisites
- Load environment variables with `direnv allow` (including `OPENAI_API_KEY`).
- Create the demo environment with `./scripts/demo_setup.sh`, then run cookbooks with `.venvs/demo/bin/python`.

## Run
- `.venvs/demo/bin/python cookbook/02_agents/human_in_the_loop/confirmation_with_session_state.py`
