# run_control

Examples for retries, cancellation, serialization, limits, metrics, and execution controls.

## Files
- `agent_serialization.py` - Demonstrates agent serialization.
- `cancel_run.py` - Demonstrates cancel run.
- `combined_metrics.py` - Combined eval, memory, and tool metrics in a single run.
- `concurrent_execution.py` - Demonstrates concurrent execution.
- `culture_metrics.py` - Culture manager metrics tracked under "culture_model" detail key.
- `debug.py` - Demonstrates debug.
- `metrics.py` - Run, message, and session metrics with tools.
- `multi_model_metrics.py` - Multi-model detail breakdown (model vs memory_model).
- `retries.py` - Demonstrates retries.
- `session_metrics.py` - Session-level metrics accumulated across multiple runs.
- `streaming_metrics.py` - Capturing metrics from streaming responses with per-model details.
- `tool_call_limit.py` - Demonstrates tool call limit.
- `tool_call_metrics.py` - Tool execution timing and per-model detail breakdown.
- `tool_choice.py` - Demonstrates tool choice.

## Prerequisites
- Load environment variables with `direnv allow` (including `OPENAI_API_KEY`).
- Create the demo environment with `./scripts/demo_setup.sh`, then run cookbooks with `.venvs/demo/bin/python`.
- Some examples require optional local services (for example pgvector) or provider-specific API keys.

## Run
- `.venvs/demo/bin/python cookbook/02_agents/run_control/<file>.py`
