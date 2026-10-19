# Moriarty

Moriarty is a playground for learning about, experimenting with, and comparing agentic-system designs. You build a crew of agents, run it against a fixed world, and get a scorecard instead of a demo.

The world is a starship. A simulation plays scenario beats with hidden causes; the crew sees only readings from mocked ship systems, investigates and acts through them under approval rules, consults an archive of prior incidents, and talks on a comms channel a human can watch. The Ship, not the crew, judges whether the incident was resolved.

Because the Ship is a fixed environment with a documented wire contract, any crew architecture or framework can be plugged in, and comparisons (choreography vs. orchestration, local vs. remote models, with and without retrieval, before and after a model upgrade) come out as evidence. The starship stands in for any operation where agents correlate telemetry into cases, act through systems of record, and are judged on outcomes they cannot self-report; the mapping is after the layer model.

## Running locally

What exists today: the local infrastructure (RabbitMQ, Postgres with pgvector, an OpenTelemetry collector, Jaeger) and the Python workspace. There is no crew, no ship system and no UI yet.

```sh
uv python install 3.14
uv sync --all-packages
cp infra/.env.example infra/.env   # then replace the placeholders
docker compose -f infra/docker-compose.yml --env-file infra/.env up -d
uv run pytest
```

Developer tooling is documented in [AGENT.md](AGENT.md). The design is in [docs/architecture.md](docs/architecture.md).
