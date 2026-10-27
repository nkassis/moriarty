# Moriarty

Moriarty is a playground for learning about, experimenting with, and comparing agentic-system designs. You build a crew of agents, run it against a fixed world, and get a scorecard instead of a demo.

The world is a starship. A simulation plays scenario beats with hidden causes; the crew sees only readings from mocked ship systems, investigates and acts through them under approval rules, consults an archive of prior incidents, and talks on a comms channel a human can watch. The Ship, not the crew, judges whether the incident was resolved.

Because the Ship is a fixed environment with a documented wire contract, any crew architecture or framework can be plugged in, and comparisons (choreography vs. orchestration, local vs. remote models, with and without retrieval, before and after a model upgrade) come out as evidence. The starship stands in for any operation where agents correlate telemetry into cases, act through systems of record, and are judged on outcomes they cannot self-report; the mapping is after the layer model.

## Running locally

What exists today: the local infrastructure (RabbitMQ, Postgres with pgvector, an OpenTelemetry collector, Jaeger), the logical clock, and the spine from the simulation through the bus to the Ship's relay. A run seeds the world, ticks the clock, and emits one lifeform-mismatch reading at tick 10, which the relay validates and publishes on `subspace`. There is no crew and no ship system yet. `bridge/` holds the Mycroft design system as React components and a `/kit` page that renders them; the bridge screens themselves come later (see [bridge/AGENT.md](bridge/AGENT.md)).

```sh
uv python install 3.14
uv sync --all-packages
cp infra/.env.example infra/.env   # then replace the placeholders
docker compose -f infra/docker-compose.yml --env-file infra/.env up -d
uv run pytest
```

Watch a run end to end:

```sh
uv run --env-file infra/.env python -m ship.relay &                 # leave running
uv run --env-file infra/.env python -m holodeck.run --mode ratio    # or --mode lockstep
```

Jaeger at http://localhost:16686 shows one trace per run: service `holodeck`, operation `run`.

Developer tooling is documented in [AGENT.md](AGENT.md). The design is in [docs/architecture.md](docs/architecture.md); the decisions behind it, with the alternative and cost of each, are in [docs/decisions-m0.md](docs/decisions-m0.md).

## License

MIT, see [LICENSE](LICENSE). Third-party dependency licenses are listed in [docs/licenses.md](docs/licenses.md).
