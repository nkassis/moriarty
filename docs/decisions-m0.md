# M0 decisions

Binding answers to the questions raised before M0 code was written. Where one changes the contract, `docs/architecture.md` carries it. Numbers match the questions as asked and are never reused.

Entries are held to the bar in `.claude/rules/decision-log.md`: a competent engineer could have chosen otherwise, reversing would cost more than a day, and each entry names the alternative and the cost. `tests/test_decision_log.py` checks the shape.

## Clock

### 3. The clock lives in the Holodeck, not the Ship

**Why:** A tick is simulation time: the layer that advances hidden state on a tick must also emit it, or every tick needs a round trip between layers. The Ship's ownership is enforcement: crews cannot influence the clock, and the Ship stamps and verifies `ship_time` on everything crews see.

**Instead of:** a clock service in `ship/`, the literal reading of "the Ship owns the clock". It would have to tell the Holodeck to advance and wait for it on every tick.

**Cost:** the Ship trusts the Holodeck's tick stream. A Holodeck ordering bug reaches the relay, which can reject a reading but not repair it.

**Status:** Accepted.

### 5. The first tick is 1, and `ship_time` counts ticks elapsed

**Why:** A reading emitted at tick 10 carries `ship_time` 10, and one tick is one ship second, so `HH:MM:SS` renders elapsed ship time with no offset.

**Instead of:** zero-based ticks, where the first tick is 0 and the tick number and elapsed time differ by one everywhere they meet.

**Cost:** `ship_time` 0 is run start, but no tick carries it. Episode triggers written `{"at": 0}` (architecture § Holodeck and episodes) must mean "at run start", and the M7 parser has to define that.

**Status:** Accepted.

### 6. A station is idle for tick N only if it reported idle after tick N went out

**Why:** In lockstep, a station that was idle before tick N arrived has not seen tick N yet. Counting that report would advance the clock past events the station never processed.

**Instead of:** the last reported state per station. Simpler, but the clock can race ahead of a slow station between ticks, which defeats lockstep.

**Cost:** every station reports after every tick, even with nothing to do: one message per station per tick. With no stations registered nothing gates the clock, so it is held to a 10 ms minimum interval rather than a hot loop.

**Status:** Accepted.

### 7. A lockstep tick advances when the wall budget expires, even if stations are busy

**Why:** One hung model call must not freeze a season. The budget is configurable, default 2.0 s; the clock records which stations missed each tick, which becomes a scorecard column.

**Instead of:** waiting indefinitely. Fully deterministic, but a stuck station stalls the run.

**Cost:** determinism now depends on model latency. A station that misses the budget sees tick N+1's state, so a slow run can diverge from a fast one under the same seed. The 2.0 s default is a guess; tuning against real model latency at M2 confirms or replaces it.

**Status:** Accepted.

### 8. Ratio mode never skips a tick and caps catch-up at 10 ticks

**Why:** Every tick can carry state changes and beat triggers; skipping one skips events the crew should see. After a stall the clock emits missed ticks back to back, but unbounded catch-up would hit crews with a burst, so `max_catchup_ticks` (default 10) caps it and the rest of the deficit is logged and dropped. Paused wall time does not count.

**Instead of:** jumping to the current wall-clock tick, which keeps ship time aligned with wall time but loses events.

**Cost:** after a stall longer than 10 ticks, ship time falls behind wall time for good. Ratio mode is a rate, not a wall-clock guarantee.

**Status:** Accepted.

## Relay and readings

### 4. The relay is a single-active consumer on the Holodeck exchange

**Why:** Ticks and readings must reach the Ship in the order the Holodeck emitted them, or a reading can arrive stamped with a `ship_time` the Ship has not reached.

**Instead of:** competing consumers, the RabbitMQ default and faster. Ordering across consumers needs sequence numbers and a reorder buffer on the Ship side, which is more code than M0 throughput justifies.

**Cost:** the relay is a single point of serialization. If it becomes the bottleneck, partition by `run_id`, since ordering only matters within a run.

**Status:** Accepted.

### 11. A reading's `source` is a closed enum of system names

**Why:** `source` and the MCP server names name the same systems. As an enum, a reading from an unknown system fails validation and goes to `lost-hail` instead of being accepted under a misspelled name.

**Instead of:** free text, which lets a new system emit readings without a contract change.

**Cost:** adding a ship system is a contract change: a row in `docs/vocabulary.md`, the enum, and regenerated schemas.

**Status:** Accepted.

## Contract and schema

### 12. Contract enums are hand-written and checked against the vocabulary by a test

**Why:** `docs/vocabulary.md` is canonical. A test that parses its enum table and fails on any difference gives that guarantee without a build step.

**Instead of:** generating `ship/contract/enums.py` from the Markdown table. Same guarantee, but it puts a Markdown parser and a generated file in the build path.

**Cost:** an enum change is two edits, table and code. The test reports the drift; a person fixes both sides.

**Status:** Accepted.

### 13. `world.persons` records who is expected; sensors report who is detected

**Why:** The lifeform-mismatch reading compares `expected_present` from the manifest with `detected_count` from the sensor view. Keeping the two apart lets M7 add unlisted lifeforms and sensor noise to detection without touching the manifest. The observable view drops `flags`, which hold hidden truth.

**Instead of:** deriving both counts from the same rows. Simpler, but then the manifest and the sensors can never disagree, and that disagreement is the scenario.

**Cost:** there are two answers to "how many people are in this section". A system that reads the wrong one gets a plausible, wrong number.

**Status:** Accepted.

## Observability

### 14. One trace per run, with each tick as a span under it

**Why:** Debugging a run means following tick 10's chain (Holodeck emit, bus publish, relay consume and validate, publish on `subspace`, consumer) as one tree under its tick. The integration test checks this tree.

**Instead of:** one trace per message flow, the usual shape for messaging. It loses the tick as the parent and scatters a run across one trace per reading.

**Cost:** a trace grows with the run, and a long ratio-mode run is one very large trace. That trace viewers handle this poorly is a guess, unmeasured so far. Incidents (M2) get their own roots linked to the run trace, so cross-incident views follow links, not parentage.

**Status:** Accepted.

## Infrastructure

### 15. The default RabbitMQ user is an administrator

**Why:** The Ship creates per-crew users with topic permissions at M3, which needs the `administrator` tag. Crew users get only the topic permissions in `docs/architecture.md`.

**Instead of:** a separate provisioning user held only by the Ship, with `moriarty` unprivileged. With no crew users to provision in M0, a second credential pair in `infra/.env` buys nothing yet.

**Cost:** every process holding the `moriarty` credentials can administer the broker, so a leaked `infra/.env` is a broker compromise. Revisit before crews run outside Compose.

**Status:** Accepted.

### 16. M0 has no remote; work happens on local branches

No remote in M0. Work on `m0/scaffold` and `m0/behaviour`; stop for review after each.

**Status:** Superseded by PR #1 and #2: the repo has a remote, and changes land on `main` by pull request (`docs/security.md` § Rules).

Retired: 9, 10, 17. Questions 1 and 2 were never recorded here.
