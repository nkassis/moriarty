# Moriarty

Moriarty is a playground for learning about, experimenting with, and comparing agentic-system designs. You build a crew of agents, run it against a fixed world, and get a scorecard instead of a demo.

The world is a starship. A simulation plays scenario beats with hidden causes; the crew sees only readings from mocked ship systems, investigates and acts through them under approval rules, consults an archive of prior incidents, and talks on a comms channel a human can watch. The Ship, not the crew, judges whether the incident was resolved.

Because the Ship is a fixed environment with a documented wire contract, any crew architecture or framework can be plugged in, and comparisons (choreography vs. orchestration, local vs. remote models, with and without retrieval, before and after a model upgrade) come out as evidence. The starship stands in for any operation where agents correlate telemetry into cases, act through systems of record, and are judged on outcomes they cannot self-report; the mapping is after the layer model.

## Running locally

What exists today: the local infrastructure (RabbitMQ, Postgres with pgvector, an OpenTelemetry collector, Jaeger), the logical clock, and the spine from the simulation through the bus to the Ship's relay. A run seeds the world, ticks the clock, and emits one lifeform-mismatch reading at tick 10, which the relay validates and publishes on `subspace`. There is no crew, no ship system and no UI yet.

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

Developer tooling is documented in [AGENT.md](AGENT.md). The design is in [docs/architecture.md](docs/architecture.md).

## Decisions

The binding design decisions, with the alternative and cost of each. M0: [docs/decisions-m0.md](docs/decisions-m0.md).

- [3. The clock lives in the Holodeck, not the Ship](docs/decisions-m0.md#3-the-clock-lives-in-the-holodeck-not-the-ship)
- [4. The relay is a single-active consumer on the Holodeck exchange](docs/decisions-m0.md#4-the-relay-is-a-single-active-consumer-on-the-holodeck-exchange)
- [5. The first tick is 1, and `ship_time` counts ticks elapsed](docs/decisions-m0.md#5-the-first-tick-is-1-and-ship_time-counts-ticks-elapsed)
- [6. A station is idle for tick N only if it reported idle after tick N went out](docs/decisions-m0.md#6-a-station-is-idle-for-tick-n-only-if-it-reported-idle-after-tick-n-went-out)
- [7. A lockstep tick advances when the wall budget expires, even if stations are busy](docs/decisions-m0.md#7-a-lockstep-tick-advances-when-the-wall-budget-expires-even-if-stations-are-busy)
- [8. Ratio mode never skips a tick and caps catch-up at 10 ticks](docs/decisions-m0.md#8-ratio-mode-never-skips-a-tick-and-caps-catch-up-at-10-ticks)
- [11. A reading's `source` is a closed enum of system names](docs/decisions-m0.md#11-a-readings-source-is-a-closed-enum-of-system-names)
- [12. Contract enums are hand-written and checked against the vocabulary by a test](docs/decisions-m0.md#12-contract-enums-are-hand-written-and-checked-against-the-vocabulary-by-a-test)
- [13. `world.persons` records who is expected; sensors report who is detected](docs/decisions-m0.md#13-worldpersons-records-who-is-expected-sensors-report-who-is-detected)
- [14. One trace per run, with each tick as a span under it](docs/decisions-m0.md#14-one-trace-per-run-with-each-tick-as-a-span-under-it)
- [15. The default RabbitMQ user is an administrator](docs/decisions-m0.md#15-the-default-rabbitmq-user-is-an-administrator)

## License

MIT, see [LICENSE](LICENSE). Third-party dependency licenses are listed in [docs/licenses.md](docs/licenses.md).
