# AGENTS.md

Stack and developer tooling, for every coding agent. Commands run from the repo root. Project rules, the architecture pointers and the current milestone are in `CLAUDE.md`; read it too.

## Stack and tooling

- Python, most recent stable. `uv` for project and dependency management. `ruff` (lint and import order) and `black` (format); both run in CI and in pre-commit. `pytest`, with `testcontainers` for anything that needs RabbitMQ or Postgres. Type hints everywhere; `pydantic` models are the schema source of truth and generate JSON Schema into `ship/contract/schema/`.
- TypeScript, strict. Contract types are generated from the same JSON Schemas; never hand-written. Vitest and React Testing Library for the unit set; Playwright for end-to-end flows named in `docs/user-stories.md`.
- Agents: any runtime per crew. Reference crews use LangGraph with LangChain adapters.
- Messaging: RabbitMQ, topic exchange `subspace`, per-crew users with topic permissions, quorum queues, dead-letter queue `lost-hail`.
- Storage: Postgres with pgvector; schemas `world` and `ship`. Redis only inside crews that want it.
- Observability: OpenTelemetry from M0. `traceparent` rides in AMQP headers and the comms envelope.
- Models: all calls go through the gateway (`ship/gateway`, FastAPI in front of LiteLLM). Crews never hold provider keys. Ollama is reached via its native chat API.
- Local: Docker Compose with profiles per crew and drive mode. Kubernetes is a later, separate track.

## Setup

```sh
uv python install 3.14
uv sync --all-packages
uv run pre-commit install --hook-type pre-commit --hook-type pre-push
cp infra/.env.example infra/.env   # then replace the placeholders
```

The pre-push hook runs TruffleHog and needs the binary on `PATH`; install it per `docs/security.md` § Local setup.

Workspace members (`holodeck`, `ship`) are virtual uv projects: modules import from the repo root. Always sync with `--all-packages`; a plain `uv sync` removes member dependencies.

## Check

```sh
uv run ruff check . && uv run black --check . && uv run pytest
```

Run it before declaring anything done. Tests marked `integration` start RabbitMQ or Postgres through testcontainers and need a running Docker daemon. Skip them with `-m "not integration"`.

## Contract schemas

```sh
uv run python -m ship.contract.generate
```

Writes JSON Schema to `ship/contract/schema/`. CI fails if the committed files differ from the output.

## Bridge

The React UI lives in `bridge/` with its own tooling (pnpm, Vite, Vitest, Playwright): see [bridge/AGENT.md](bridge/AGENT.md). Quick check from the repo root: `pnpm -C bridge check`.

## Run the spine

```sh
uv run --env-file infra/.env python -m ship.relay                   # the relay; leave running
uv run --env-file infra/.env python -m holodeck.run --mode ratio    # --mode lockstep, --ratio K, --ticks N, --seed S
```

Both need `AMQP_URL` and `DATABASE_URL` (see `infra/.env.example`); spans go to `OTEL_EXPORTER_OTLP_ENDPOINT`. The relay's queue is declared by either process, so start order does not matter. Traces: Jaeger, service `holodeck`, operation `run`.

## Local stack

```sh
docker compose -f infra/docker-compose.yml --env-file infra/.env up -d
docker compose -f infra/docker-compose.yml --env-file infra/.env down        # keep volumes
docker compose -f infra/docker-compose.yml --env-file infra/.env down -v     # drop volumes
```

| Service | Port | URL |
| --- | --- | --- |
| RabbitMQ AMQP | 5672 | |
| RabbitMQ management | 15672 | http://localhost:15672 |
| RabbitMQ Prometheus | 15692 | http://localhost:15692/metrics |
| Postgres (pgvector) | 5432 | |
| OTel collector (OTLP gRPC, HTTP) | 4317, 4318 | |
| Jaeger UI | 16686 | http://localhost:16686 |
