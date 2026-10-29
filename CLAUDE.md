# Moriarty

A playground for learning about, experimenting with, and comparing agentic-system designs. A simulated starship (the Holodeck) plays scenario beats with hidden causes; crews of LLM agents see only readings from mocked ship systems, act through them under approval rules, and are judged by the Ship against hidden truth. The point is the Ship contract: any crew architecture plugs in and is scored on the same seeded scenarios.

Read `docs/architecture.md` before any work on `holodeck/`, `ship/` or `crews/`. It is the source of truth until `spec.md` exists; contract changes land in it in the same PR as the code. `docs/decisions-<milestone>.md` files hold binding answers to the questions each milestone raised; the current one wins over the architecture doc for that milestone, and the doc is fixed to match.

`AGENTS.md` holds the stack and developer tooling (setup, lint, tests, compose, schema generation) for every coding agent and is imported here:

@AGENTS.md

## Current milestone

M1: First light (v0.1). See `docs/architecture.md` § Milestones for the definition of done, `docs/decisions-m1.md` for the binding answers and `docs/kickoff-m1.md` for the branches. Do not start M2+ work in an M1 PR.

## Layers and the boundary

- `holodeck/` owns truth and the clock. It writes the `world` schema; nothing else does.
- `ship/` owns the bus, the MCP systems, the Incident Desk, the archive, the gateway, the API. Systems read `world` through observable views only.
- `crews/` reach the Ship only over the network: AMQP, MCP, the gateway URL. A crew holds no Ship credentials. Nothing in `ship/` imports from `crews/`.
- The Holodeck never reads comms or crew output. It reacts to the internal action stream only.

## Vocabulary

Code, schemas, file names and the contract use plain names: `gateway`, `chaos`, `budget`, `archive`, `simulation`. Themed names (Warp Core, Continuum, Dilithium, Holodeck, Mycroft) are display labels for the bridge and README flavor. `docs/vocabulary.md` is the canonical table; the enums in `ship/contract` are hand-written and a test fails on any difference from it. No franchise ship names, character names, registry numbers, insignia or stardates anywhere. Ship time is integer ticks, rendered `HH:MM:SS`.

Contract enums are fixed; do not invent new values without a doc change:
- Agent state: `idle`, `thinking`, `acting`, `standby`
- Incident state: `open`, `investigating`, `acting`, `awaiting_captain`, `closed`
- Outcome: `win`, `partial`, `fail`, `escalated`
- Comms kind: `request`, `report`, `ack`, `order`, `escalation`, `system`
- Division: `command`, `ops`, `science`
- Tool errors: `unavailable`, `timeout`, `stale`, `partial`, `requires_authorization`, `not_allowed`; every error carries `retryable` and, when retryable, `retry_after` in ticks

## Conventions

- One PR per milestone or per parallel track within a milestone. The PR description names the milestone and the user stories it closes.
- A milestone is done when its definition of done in `docs/architecture.md` is met and a test proves it.
- Every action tool takes an `idempotency_key`; a replayed key returns the recorded result.
- Tool results are the few fields that matter. Verbose tool output is a bug.
- No prose narration from agents; tool calls and a structured `file_report` only.
- Docs follow the writing standard in `docs/architecture.md` § Developer documentation: technical register, one fact in one place, concise, real examples, draft then tighten then independent review.
- Commit messages: imperative, one line, body only when the why is not obvious.

## Repo layout

See `docs/architecture.md` § Tech stack and repo layout. Create directories only when the milestone needs them.

## Working with coding agents

- Read the milestone's definition of done and the relevant user stories before writing code.
- When a design question is not answered by `docs/architecture.md`, stop and ask rather than deciding silently; record the answer in the doc's Open decisions section.
- Run the check in `AGENTS.md` § Check before declaring anything done.
- Do not add dependencies without saying why in the PR.

## Claude Code hooks

`.claude/settings.json` runs these; a blocking hook (exit 2) feeds its message back until the problem is fixed:
- **PreToolUse** (Bash): `.claude/hooks/guard-bash.sh` blocks committing on main, pushing to main, force pushing anywhere and deleting main. It reads the command line, so it catches mistakes, not bypasses.
- **PostToolUse** (Edit/Write): `.claude/hooks/check-python.sh edit` runs Black on the edited Python file, then Ruff; findings block.
- **Stop**: `.claude/hooks/check-python.sh stop` runs `ruff check .` before Claude may finish.
- **Read deny list**: `.env` variants, `*.pem`, `*.key`, `~/.ssh` and `~/.aws` are unreadable; `infra/.env.example` stays readable.

The hooks need `uv`; `jq` is used if present, else `python3`. Bridge files have no Claude hook yet; the bridge pre-commit hooks and CI cover them.

## Linear

Work is tracked in Linear (team NIM, project Moriarty). Issue keys look like NIM-12.

When a task has a Linear issue (or you can find one that matches), follow this flow:

1. Before starting, move the issue to **In Progress** and work on a branch that
   contains the issue key, e.g. `nim-12-gateway-contract`.
2. Put the issue key in commit messages (`NIM-12: add gateway contract types`).
3. When the work is done and tests pass, push the branch and open a PR with
   `gh pr create`. Put the key in the PR title and `Closes NIM-12` in the body
   (`Refs NIM-12` if the PR only covers part of the issue).
4. Then update the issue through the Linear MCP tools:
   - link the PR URL on the issue (`save_issue` with `links`; `create_attachment` uploads files, not links)
   - add a short comment: what changed, how it was verified, anything left open
   - move the issue to **In Review**
5. Never move an issue to Done yourself. That happens when the PR merges.

If the task has no Linear issue, ask whether to create one before opening the PR.
