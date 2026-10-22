# AGENT.md

Developer tooling. Commands run from the repo root.

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

Tests marked `integration` start RabbitMQ or Postgres through testcontainers and need a running Docker daemon. Skip them with `-m "not integration"`.

## Contract schemas

```sh
uv run python -m ship.contract.generate
```

Writes JSON Schema to `ship/contract/schema/`. CI fails if the committed files differ from the output.

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
