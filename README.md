# one-founder-studio-crew

**One founder, a crew of AI agents.** A solo founder tells a Band room what to build. A Planner, Builder, Reviewer and Sentinel (security lead) share one plan, hand work to each other, remember what they learn, and ask the founder only when a real decision is needed.

## The problem
Solo founders spend their time copying context between coding agents and chatbots instead of shipping. Agent-written code also ships fast, and so do its vulnerabilities, and each new session forgets what the last one learned.

## The agent team (Band Desktop room)
| Agent | Role | Harness | Hands off to |
|---|---|---|---|
| **Planner** | Recalls memory, writes one numbered plan | Band SDK, LangGraph adapter, DeepSeek | Builder |
| **Builder** | Writes backend/frontend code in `workspace/` | same | Reviewer |
| **Reviewer** | Reviews code, stores lessons | same | Sentinel |
| **Sentinel** | Runs Snyk Code, gates "Done", asks the founder to ship or block, bills the work item | same | Founder / Builder |

All four join one Band room ("My AI-startup room"). Handoffs are @mentions in the room; Band keeps the shared record. The founder is the only human and is asked only for real decisions (for example, ship despite a finding).

## How Cognee memory is used
Every agent shares one Cognee knowledge graph (`studio_memory`, DeepSeek for extraction, Gemini embeddings):
- **Reviewer and Sentinel `remember`** review findings, vulnerability patterns and their fixes (for example, a path traversal Snyk found in an agent-written endpoint).
- **Planner and Builder `recall` before planning or writing code**, so the next feature starts from "From memory: ..." instead of repeating the mistake. Memory persists across sessions.

## How Snyk is used
Sentinel runs `snyk code test` on the workspace before any item is Done. On a real run Snyk Code flagged a **HIGH Path Traversal** in agent-written code; Builder fixed it, a re-scan came back clean, and the pattern was stored in Cognee.

## How Flexprice is used
Each work item that passes the gate (or that the founder approves) sends one `agent_task_completed` usage event to Flexprice for the customer's project (`crew/billing.py`). The 'studio crew' Count meter and the 'studio builds' plan turn builds into usage-based billing per customer project.

## Run it
```bash
cd studio-crew
uv sync
cp .env.example .env   # DEEPSEEK_API_KEY, GEMINI_API_KEY, BAND_USER_API_KEY, FLEXPRICE_*; see below
# register four Band agents (Planner, Builder, Reviewer, Sentinel) -> agent_config.yaml
uv run python -m crew.run_agent   # all four agents in ONE process (Cognee's graph DB is single-process)
```
Then add the four agents to a Band room and send: `@Planner add a /settings endpoint that reads user-supplied YAML`.

Cognee needs `STRUCTURED_OUTPUT_FRAMEWORK=instructor` and `LLM_INSTRUCTOR_MODE=json_mode` with DeepSeek. Snyk needs `snyk auth` and Snyk Code enabled for the org.

## Layout
`crew/run_agent.py` runs the agents · `crew/roles.py` role prompts · `crew/tools.py` memory, files, Snyk and billing tools · `crew/billing.py` Flexprice events.
