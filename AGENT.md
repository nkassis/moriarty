# AGENT.md

Developer tooling. Commands run from the repo root.

## Setup

```sh
uv python install 3.14
uv sync --all-packages
uv run pre-commit install
cp infra/.env.example infra/.env   # then replace the placeholders
```

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
