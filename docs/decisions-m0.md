# M0 decisions

Answers to the questions raised before M0 code was written. Each is binding for M0; where it changes the contract, `docs/architecture.md` already carries it. Numbering matches the questions as asked.

## Clock

**3. Ownership.** The clock is simulation time, so the code lives in `holodeck.clock`. "The Ship owns the clock" means crews cannot influence it and the Ship stamps and verifies `ship_time` on everything crews see.

**5. Tick numbering.** A run starts at 0. The first `clock.tick` carries 1. A reading emitted at tick 10 has `ship_time` 10. One tick is one ship second.

**6. Lockstep with no stations.** Keep an in-memory registry of stations that report state. A station counts as idle for tick N only if it reported idle after tick N went out. With no stations registered the clock still honours a minimum tick interval (10 ms); never a hot loop.

**7. Wall budget.** Configurable, default 2.0 s. When it expires the tick advances and the clock records which stations missed it; that count becomes a scorecard column later.

**8. Ratio mode.** k means k ticks per wall second, default 1. Ticks are emitted one by one and never skipped. Catch-up after a stall is capped by `max_catchup_ticks` (default 10); beyond that the deficit is logged and dropped. Wall time spent paused does not count.

**9. Captain pause.** The `awaiting_captain` predicate is a stub returning false. The clock keeps a running total of paused wall time, internal only in M0.

**10. Tick message.** `{run_id, ship_time, mode}`. `traceparent` in AMQP headers only.

## Relay and readings

**4. Ordering.** The Holodeck publishes ticks and raw readings to one internal exchange, `holodeck`, and stamps `ship_time` on each reading as it emits it. The relay is a singleton consumer (single-active-consumer) on one queue bound to that exchange, so the Holodeck's order is the relay's order. It forwards ticks to `subspace` as `clock.tick`, validates each reading, verifies the reading's `ship_time` equals the current tick (a mismatch raises and dead-letters; the relay never corrects a stamp), stamps `event_id`, `run_id`, `wall_time` and `traceparent`, publishes on `subspace`, and acks only after publishing. Crews cannot read `clock.*` or the `holodeck` exchange.

**11. RawObservation.** `{routing_key, source, severity, observed, ship_time}`. `source` is an enum of the system names (`sensors`, `manifest`, `bulkheads`, `security`, `sickbay`, `engineering`, `librarian`, `comms`), not free text, because the MCP server names and this field name the same thing. `severity` is 1 to 5, 5 most severe. `observed` is validated against a schema per routing key; M0 defines one, `lifeform_mismatch`: `{deck, section, expected_count, detected_count}`. Unknown routing keys and invalid payloads go to `lost-hail`.

## Contract and schema

**12. Enums.** Hand-written in Python, with a test that reads the enum table in `docs/vocabulary.md` and fails if the two differ. `vocabulary.md` is canonical (eleven enums); `architecture.md` is fixed to match in the same PR. TypeScript types wait for M1.

**13. `world.persons`.** `world.persons(run_id, person_id, name, kind, deck, section, flags, expected_present)`. `kind` is an enum (`crew`, `passenger`, `unlisted`). `expected_present` is what the lifeform-mismatch reading counts against; `detected_count` comes from the sensor view, which in M7 will include unlisted lifeforms and noise. Sections are the distinct `(deck, section)` pairs. The observable view drops `flags`. SQL in `ship/world/sql/`, applied at run start; a migration tool arrives with the second table.

## Observability

**14. Trace shape.** One trace per run, rooted at run start. Each tick is a span under it; tick 10's chain (Holodeck emit, bus publish, relay consume and validate, publish on subspace, test consumer) hangs under the tick-10 span. The integration test checks this tree. Incidents get their own root linked to the run trace when the Incident Desk arrives in M2.

## Infrastructure

**15. RabbitMQ user.** `moriarty` is the default user, credentials from `infra/.env` with a committed `.env.example`. It has the `administrator` tag because it creates crew users in M3; crew users get only the topic permissions in `docs/architecture.md`. Topology is declared in code; quorum queues with delivery limit 5, dead-lettered to `lost-hail`.

**16. Branches.** No remote in M0. Work on `m0/scaffold` and `m0/behaviour`; stop for review after each.

**17. Housekeeping.** Delete `moriarty-docs.zip:Zone.Identifier` (a Windows download artefact; it does not belong in the tree). Widen `.gitignore` to `.env.*` keeping `.env.example`. Add `AGENT.md` for dev tooling; `CLAUDE.md` stays the project brief and points at it.

## Settled elsewhere

- Episodes, beats and seasons are JSON (`*.beat.json`, `*.episode.json`, `*.season.json`), validated by the contract's pydantic models.
- The Holodeck stays in Python; see `docs/architecture.md` § Open decisions.
- `wall_time` rides beside `ship_time` on events and action-stream entries, for time-to-action; never for judgment.
