# Test Log: run_control

> Updated: 2026-02-17

### agent_serialization.py

**Status:** PASS

**Description:** Executed as a cookbook runnable example.

**Result:** Completed successfully.

---

### cancel_run.py

**Status:** PASS

**Description:** Executed as a cookbook runnable example.

**Result:** Completed successfully.

---

### combined_metrics.py

**Status:** PASS

**Description:** Combined eval, memory, and tool metrics in a single run with detail key breakdown.

**Result:** Shows model, memory_model, and eval_model detail keys with token counts. Detail sum matches total.

---

### concurrent_execution.py

**Status:** PASS

**Description:** Executed as a cookbook runnable example.

**Result:** Completed successfully.

---

### culture_metrics.py

**Status:** PASS

**Description:** Culture manager metrics tracked under "culture_model" detail key.

**Result:** Shows model and culture_model detail keys with separate token counts.

---

### debug.py

**Status:** PASS

**Description:** Executed as a cookbook runnable example.

**Result:** Completed successfully.

---

### metrics.py

**Status:** PASS

**Description:** Run, message, and session metrics with tools.

**Result:** Completed successfully.

---

### multi_model_metrics.py

**Status:** PASS

**Description:** Multi-model detail breakdown showing model vs memory_model tokens.

**Result:** Shows model and memory_model detail keys with separate token counts.

---

### retries.py

**Status:** PASS

**Description:** Executed as a cookbook runnable example.

**Result:** Completed successfully.

---

### session_metrics.py

**Status:** PASS

**Description:** Session-level metrics accumulated across multiple runs with PostgreSQL.

**Result:** Shows per-run metrics and accumulated SessionMetrics with ModelMetrics details.

---

### streaming_metrics.py

**Status:** PASS

**Description:** Capturing metrics from streaming responses with per-model detail breakdown.

**Result:** Shows streaming run metrics with ModelMetrics details including provider and time_to_first_token.

---

### tool_call_limit.py

**Status:** FAIL

**Description:** Executed as a cookbook runnable example.

**Result:** Failed with Anthropic API authentication error (401 Unauthorized). Environment issue -- ANTHROPIC_API_KEY is invalid.

---

### tool_call_metrics.py

**Status:** PASS

**Description:** Tool execution timing and per-model detail breakdown.

**Result:** Shows run metrics, ToolCallMetrics with duration for each tool call, and ModelMetrics details.

---

### tool_choice.py

**Status:** FAIL

**Description:** Executed as a cookbook runnable example.

**Result:** Failed with Anthropic API authentication error (401 Unauthorized). Environment issue -- ANTHROPIC_API_KEY is invalid.

---
