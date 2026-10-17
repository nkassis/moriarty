# Moriarty

A playground for learning about, experimenting with, and comparing agentic-system designs. A simulated starship (the Holodeck) plays scenario beats with hidden causes; crews of LLM agents see only readings from mocked ship systems, act through them under approval rules, and are judged by the Ship against hidden truth. The point is the Ship contract: any crew architecture plugs in and is scored on the same seeded scenarios.

Read `docs/architecture.md` before any work on `holodeck/`, `ship/` or `crews/`. It is the source of truth until `spec.md` exists; contract changes land in it in the same PR as the code. `docs/decisions-<milestone>.md` files hold binding answers to the questions each milestone raised; the current one wins over the architecture doc for that milestone, and the doc is fixed to match.

## Current milestone

M0: spine and clock. See `docs/architecture.md` § Milestones for the definition of done. Do not start M1 work in an M0 PR.

## Layers and the boundary

- `holodeck/` owns truth and the clock. It writes the `world` schema; nothing else does.
- `ship/` owns the bus, the MCP systems, the Incident Desk, the archive, the gateway, the API. Systems read `world` through observable views only.
- `crews/` reach the Ship only over the network: AMQP, MCP, the gateway URL. A crew holds no Ship credentials. Nothing in `ship/` imports from `crews/`.
- The Holodeck never reads comms or crew output. It reacts to the internal action stream only.

## Vocabulary

Code, schemas, file names and the contract use plain names: `gateway`, `chaos`, `budget`, `archive`, `simulation`. Themed names (Warp Core, Continuum, Dilithium, Holodeck, Mycroft) are display labels for the bridge and README flavor. `docs/vocabulary.md` is the canonical table; `ship/contract` generates its enums from it. No franchise ship names, character names, registry numbers, insignia or stardates anywhere. Ship time is integer ticks, rendered `HH:MM:SS`.

Contract enums are fixed; do not invent new values without a doc change:
- Agent state: `idle`, `thinking`, `acting`, `standby`
- Incident state: `open`, `investigating`, `acting`, `awaiting_captain`, `closed`
- Outcome: `win`, `partial`, `fail`, `escalated`
- Comms kind: `request`, `report`, `ack`, `order`, `escalation`, `system`
- Division: `command`, `ops`, `science`
- Tool errors: `unavailable`, `timeout`, `stale`, `partial`, `requires_authorization`, `not_allowed`; every error carries `retryable` and, when retryable, `retry_after` in ticks

## Stack and tooling

- Python, most recent stable. `uv` for project and dependency management. `ruff` (lint and import order) and `black` (format); both run in CI and in pre-commit. `pytest`, with `testcontainers` for anything that needs RabbitMQ or Postgres. Type hints everywhere; `pydantic` models are the schema source of truth and generate JSON Schema into `ship/contract/schema/`.
- TypeScript, strict. Contract types are generated from the same JSON Schemas; never hand-written. Vitest and React Testing Library for the unit set; Playwright for end-to-end flows named in `docs/user-stories.md`.
- Agents: any runtime per crew. Reference crews use LangGraph with LangChain adapters.
- Messaging: RabbitMQ, topic exchange `subspace`, per-crew users with topic permissions, quorum queues, dead-letter queue `lost-hail`.
- Storage: Postgres with pgvector; schemas `world` and `ship`. Redis only inside crews that want it.
- Observability: OpenTelemetry from M0. `traceparent` rides in AMQP headers and the comms envelope.
- Models: all calls go through the gateway (`ship/gateway`, FastAPI in front of LiteLLM). Crews never hold provider keys. Ollama is reached via its native chat API.
- Local: Docker Compose with profiles per crew and drive mode. Kubernetes is a later, separate track.

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
- Run `uv run ruff check . && uv run black --check . && uv run pytest` before declaring anything done.
- Do not add dependencies without saying why in the PR.
