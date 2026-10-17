# M0 kickoff prompt

Paste into the first Claude Code session in this repo, from the repo root with `CLAUDE.md` and `docs/` in place.

---

Read CLAUDE.md, then docs/architecture.md in full (it is long; read all of it), then docs/decisions-m0.md, docs/vocabulary.md and docs/user-stories.md. Do not read docs/reviews/ or docs/design/ yet.

docs/decisions-m0.md answers the questions raised in the last session. Treat it as binding for M0. If anything in it conflicts with docs/architecture.md, the decisions file wins for M0 and you fix the architecture doc in the same PR.

We are at milestone M0: spine and clock. Definition of done: a trace exists with Holodeck, bus and Ship spans, and ship_time advances in both clock modes.

Before writing code, confirm the toolchain on this machine (python3 version, uv, docker and docker compose, whether Ollama answers at localhost:11434) and report it. Install nothing without asking. If any M0 question remains that the decisions file does not answer, list it with your proposed reading and wait.

Work on two local branches off main, m0/scaffold then m0/behaviour, and stop for review after each.

m0/scaffold, no behaviour:
- git init if needed; first commit on main is the docs as they are (delete the Zone.Identifier file first).
- Monorepo layout from docs/architecture.md § Tech stack and repo layout, only what M0 needs: holodeck/, ship/bus/, ship/world/, ship/contract/, infra/, docs/. One uv workspace at the root; each Python package has its own pyproject.toml.
- Root pyproject.toml with uv workspace, ruff, black and pytest config. Python: most recent stable. Pin nothing published in the last two weeks.
- infra/docker-compose.yml: RabbitMQ (management and Prometheus plugins on), Postgres with pgvector, OTel collector, Jaeger. Named volumes. The moriarty user per decisions 15, credentials from infra/.env with a committed .env.example. A crew-net network defined with nothing on it yet.
- infra/postgres/init/: creates schemas world and ship, empty.
- .github/workflows/ci.yml: ruff, black --check, pytest, and a schema drift check that fails if ship/contract/schema/ differs from what `uv run python -m ship.contract.generate` writes.
- .pre-commit-config.yaml with ruff and black. .gitignore covering .env.* except .env.example.
- AGENT.md for dev tooling (how to run lint, tests, compose); CLAUDE.md gets one line pointing at it.
- README.md: the three Pitch paragraphs from docs/architecture.md and a "how to run" that is honest about M0.

m0/behaviour:
- ship/contract: pydantic models for Event (architecture § 1. Events, including wall_time), RawObservation and the lifeform_mismatch observed schema (decisions 11), and the clock tick message (decisions 10); enums hand-written with the vocabulary.md drift test (decisions 12); generate.py writing JSON Schema to ship/contract/schema/. Tests that schemas round-trip.
- holodeck/clock.py per decisions 3 and 5 to 9: lockstep with the station registry, the idle-after-tick rule, the 2.0 s budget and missed-station record, the minimum tick interval; ratio with k ticks per wall second, no skipped ticks, max_catchup_ticks; the awaiting_captain stub and paused-time total. Unit tests for both modes with a fake wall clock.
- holodeck/world.py: world.persons per decisions 13, SQL in ship/world/sql/ applied at run start, the observable view dropping flags.
- holodeck/run.py: starts a run with a seed, writes the manifest, emits one hard-coded alert.security.lifeform_mismatch reading at tick 10 stamped ship_time 10. Ticks and readings both go to the internal holodeck exchange.
- ship/bus: topology (exchange subspace, DLQ lost-hail, quorum queues with delivery limit 5); a publish helper that stamps event_id, run_id, wall_time and traceparent; a consume helper that restores traceparent into the OTel context.
- ship/relay.py per decisions 4: single-active-consumer on one queue bound to holodeck; forwards ticks as clock.tick; validates readings, verifies ship_time against the current tick (mismatch raises and dead-letters), stamps, publishes on subspace, acks after publish.
- OTel per decisions 14: one trace per run, a span per tick, the reading's chain under its tick span. Export to the collector.
- Integration tests with testcontainers: start a run, assert one event arrives on a test queue with a valid traceparent, ship_time 10 and a wall_time, assert ship_time advanced in lockstep and in ratio mode, assert the span tree; a second test publishes a reading stamped 9 under tick 10 and asserts the relay rejects it to lost-hail.
- Anything you had to decide beyond the decisions file goes into docs/architecture.md § Open decisions as one line each, in the same branch.

Run `uv run ruff check . && uv run black --check . && uv run pytest` before calling a branch ready. Commit messages imperative, one line.
