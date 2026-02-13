# Test Log: 09_decision_logs

> Updated: 2026-02-14

### 01_basic_decision_log.py

**Status:** PASS

**Description:** Agent with DecisionLogTool logs decisions when asked for recommendations. Tests `.learning_machine` property access (changed from `.get_learning_machine()` method).

**Result:** Agent logged a decision recommending Python for web scraping with reasoning and alternatives. Decision log displayed correctly via rich Panel. Runs in ~5s.
**Re-verified:** 2026-02-16 — Post-rebase onto main. PASS. Decision log displayed correctly with multiple entries.

---

### 02_decision_log_always.py

**Status:** PASS

**Description:** Agent with ALWAYS-mode decision logging + DuckDuckGo search tool. Agent searched for AI agent news and auto-logged decisions.

**Result:** PASS. Ran in ~15s. DDG search executed, decision log displayed (empty — ALWAYS mode logs after response, not during tool calls as expected).
**Re-verified:** 2026-02-16 — Post-rebase onto main. PASS.

---

