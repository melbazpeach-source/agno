# Test Log: metrics

> Updated: 2026-02-17

### 01_team_metrics.py

**Status:** PASS

**Description:** Team, session, and member-level execution metrics with PostgreSQL.

**Result:** Shows team leader message metrics, aggregated team metrics, session metrics, and member message metrics with token counts.

---

### 02_team_streaming_metrics.py

**Status:** PASS

**Description:** Capturing metrics from team streaming responses with per-model detail breakdown.

**Result:** Shows streaming team metrics with model detail entries including provider, tokens, and time_to_first_token.

---

### 03_team_session_metrics.py

**Status:** PASS

**Description:** Session-level metrics that accumulate across multiple team runs with PostgreSQL.

**Result:** Shows per-run metrics and accumulated session metrics with ModelMetrics details including provider and token breakdown.

---

### 04_team_tool_metrics.py

**Status:** PASS

**Description:** Tool execution timing and member-level metrics with YFinanceTools.

**Result:** Shows aggregated team metrics, member metrics, and ToolCallMetrics with duration for each tool call.

---
