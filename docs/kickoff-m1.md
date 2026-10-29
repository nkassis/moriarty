# M1 kickoff prompt

Paste into a Claude Code session at the repo root, one session per branch. Each branch has a Linear issue; follow the Linear flow in `CLAUDE.md` and use the issue's branch name. The short names below are how this document refers to them.

---

Read CLAUDE.md, then docs/architecture.md in full, then docs/decisions-m1.md, docs/decisions-m0.md, docs/vocabulary.md and docs/user-stories.md. Do not read docs/reviews/ or docs/design/.

docs/decisions-m1.md is binding for M1. If anything in it conflicts with docs/architecture.md, the decisions file wins and you fix the architecture doc in the same PR.

We are at M1: First light (v0.1). Definition of done: the video script in docs/architecture.md § Milestones runs end to end from a clean clone, twice, on two seeds. Anything the video does not need is M2+; do not build it.

Before writing code, read your branch's Linear issue and its comments, confirm the toolchain for your branch (python3, uv, docker compose; pnpm for the bridge; Ollama per decisions-m1 4 for crew-xo) and report it. Install nothing without asking. If a design question is not answered by the docs, stop and ask; record the answer in docs/architecture.md § Open decisions, or in docs/decisions-m1.md if it passes the bar in .claude/rules/decision-log.md.

Contract models land with the first branch that needs them. Tracks overlap only in `ship/contract`; rebase on main before regenerating schemas.

Your branch is one of the following. Stop for review when it is ready.

m1/holodeck-beats (NIM-16, with the episode file from NIM-15). Starts first, in parallel with m1/ship-systems.
- Doyle models in ship/contract for beats and episodes, including `clock.tick_seconds`, `captain_policy` and `debrief.reveal` in the episode header; the parser; seeded parameter distributions.
- scenarios/episodes/unlisted.episode.json and its beats, validated by those models.
- The beat engine (`when`, `emit`, `advance`) driven by the clock, reacting only to the internal action stream.
- The derived sensor view over `world.persons`, including the decoy, with the episode's noise.
- Resolution by precedence (win, partial, fail; `escalated` terminal), and the fact set the debrief reads: the truth timeline, the action stream, timings.
- Tests: "Unlisted" at two seeds; same seed, same beats.

m1/ship-systems (NIM-17, then NIM-21). Starts first, in parallel with m1/holodeck-beats.
- Contract models for the envelope, heartbeat, action event, report, incident closed, `RunConfig`, tool errors, and the messages on the bridge stream.
- MCP servers for Sensors, Manifest, Bulkheads and Security with the tools in decisions-m1 6; `idempotency_key` on every action tool; structured errors with `retryable` and `retry_after`; `reversible` and `pii` tags; `detain` gated on `order_id`; reads through observable views only.
- The Incident Desk (`open_incident`, `attach_event`, `request_order`, `file_report`, `owner`); the Captain's Chair with `hitl` and the episode policy as fallback; the clock pause while `awaiting_captain`.
- The gateway: FastAPI in front of LiteLLM, aliases `triage` and `summary`, the three headers, 402 on budget, the full-body cache key, `ollama_chat/`.
- The Ship API: `POST /runs`, run status, one stream for the bridge, the approval endpoint. The comms exchange, the action stream, a per-crew RabbitMQ user created at run start.
- Integration tests: tool idempotency, order gating, 402 on budget, a comms message delivered end to end on the stream.
- Second PR on the same track, once m1/holodeck-beats has merged the fact set: the debrief (NIM-21), with the template and `summary` renderers, `runs/<run_id>/postmortem.md`, served on the Ship API.

m1/cli (NIM-20). Starts any time; `run` waits for the Ship API.
- `moriarty` as a Typer command in the uv workspace: `up`, `down`, `status`, `logs`, `doctor`, `schema`, then `run`.
- `run <episode> [profile.json] [--seed N]` per § Configuration: `profiles/demo.json` (the default) and `profiles/eval.json`, the manifest, the seed printed first, the bridge URL, the outcome and the debrief path at the end.
- A test per command; integration tests for `doctor` and `run`.

m1/bridge (NIM-19). Starts once the stream message models are on main.
- The Live screen at `/bridge/:runId` on `bridge/src/mycroft/` and the generated contract types: status strip, station cards (standby dimmed), comms with the muted tool layer, the Captain's Chair order prompt, the outcome banner and the Captain's Log.
- Fed by the Ship API stream; reconnects and resyncs from the run's current state.
- Vitest and React Testing Library for state mapping; one Playwright flow against a recorded stream: run starts, comms appear, order approved, outcome shows. See bridge/AGENT.md.

m1/crew-xo (NIM-18). Starts once m1/ship-systems has merged.
- crews/crew-xo as its own process and compose profile on `crew-net`, holding no Ship credentials.
- XO, Ops and Security live on LangGraph; Science, Engineering and Medical heartbeat `standby` (decisions-m1 2).
- Decides whether a reading belongs to an open incident; requests an order for `detain`; handles `requires_authorization` and retryable errors.
- GenAI span conventions; `traceparent` from the consumed event; versioned prompts in crews/crew-xo/prompts/ with the prompt hash on `file_report`.
- Settle the two open decisions it owns (interrupt transport, context per turn) before building on them.
- Done when "Unlisted" ends in a win on at least one seed on the local model and on the demo model. `crew-single` is the fallback if three stations are unreliable on camera.

Run `uv run ruff check . && uv run black --check . && uv run pytest` (and `pnpm -C bridge check` for the bridge) before calling a branch ready.
