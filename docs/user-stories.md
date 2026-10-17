# User stories

One story per thing a person does on a screen or against the contract. A screen element with no story is cut; a story with no milestone is backlog. Acceptance is one line and testable (a Playwright flow, a pytest, or a conformance check). Ids: H home, S scenarios, B bridge, D director, E evaluation, C crew developer.

**Personas**

| Persona | Who | Wants |
| --- | --- | --- |
| Operator | Watches a run; acts as captain when asked | Follow an incident; approve or belay; never see hidden truth |
| Director | Runs a live session | Start beats, inject faults, control the clock, see the truth |
| Evaluator | Compares crews | Run seasons unattended; read scorecards; trust the numbers |
| Crew developer | Builds a crew | The contract, the docs, a conformance result |

## Home

| Id | As a | I want | Acceptance | Milestone |
| --- | --- | --- | --- | --- |
| H-01 | any user | a home page with navigation to Scenarios, Bridge, Director, Scorecard and the docs | Every screen is one click from home; the Rail on every screen reaches every other screen | M5 |
| H-02 | any user | to see whether a run is live and which one | Home shows the active run (episode, crew, clock mode) or "no run" | M5 |

## Scenarios

| Id | As a | I want | Acceptance | Milestone |
| --- | --- | --- | --- | --- |
| S-01 | Evaluator | to browse the season as a list of episodes with kind, beats, difficulty and best last result | Table reads from `scenarios/episodes/`; selecting a row shows its beats and triggers | M7 |
| S-02 | Evaluator | to see the beats inside an episode and when each starts | Beat name, synopsis, start trigger per row | M7 |
| S-03 | Evaluator | to choose crew, drive mode, clock mode, seed, continuum and archive state before a run | Run summary line reflects every control; the run request carries all of them | M3 (crew, seed), M7 (rest) |
| S-04 | Operator | to start an episode and be taken to the bridge with the run already live | Run starts in ratio mode; bridge opens on it within one tick | M5 |
| S-05 | Evaluator | to run one episode over N seeds unattended | Captain is the scripted `captain_policy`; run completes with no prompt; scorecard row appears | M3 |
| S-06 | Evaluator | to run the whole season unattended | Same as S-05 for every episode; progress visible; one scorecard per crew | M7 |
| S-07 | Evaluator | to create a season from a few episodes and run it automatically with a simulated captain | Season saved as a file; its episodes run in order with `captain_policy` per beat; result lands on the Scorecard | M7 |
| S-08 | Evaluator | to see the last result per crew for the selected episode | Readouts per crew from the latest held-out run | M7 |

## Bridge

| Id | As a | I want | Acceptance | Milestone |
| --- | --- | --- | --- | --- |
| B-01 | Operator | to see the alert condition and its reason | AlertBanner shows condition and detail set by the Ship; theme shift is a setting, off by default | M5 |
| B-02 | Operator | to read comms by incident or all at once, in time order | Channel tabs filter; lines sorted by `ship_time`; each line shows sender, index, kind, time | M5 |
| B-03 | Operator | to hide or show tool calls in the channel | Toggle; tool lines come from the action stream, muted | M5 |
| B-04 | Operator | to see every station, its state, and what it is doing | AgentCards from the heartbeat; stale heartbeat shows `standby` with a caption | M5 |
| B-05 | Operator | to approve or belay a pending order and see exactly what it authorizes | Pending card names tool and args; confirm dialog; the order posts to comms with an `order_id`; the tool accepts it | M4 |
| B-06 | Operator | to send a free-text order to a channel | Composer posts an `order` envelope; crews receive it as an event | M4 |
| B-07 | Operator | to see open incidents with owner, state, elapsed and links | Table from the Incident Desk; no Holodeck fields (no act) | M5 |
| B-08 | Operator | to see the timeline of a selected incident | Timeline from comms and action stream for that incident | M5 |
| B-09 | Operator | to see budget used per incident and run cost | Gauges from the gateway; a 402 shows as a system line | M5 |
| B-10 | Director | to cause chaos from the bridge by starting a beat or a continuum event | Director drawer, controls only; a fault count is shown, never which system | M7 |
| B-11 | Operator | to open the trace behind any comms line | Line carries `trace_id`; click opens the trace viewer on that run | M10 |
| B-12 | Operator | to replay a closed incident at 1x, 10x or step by step | Scrubber over the log; comms and actions replay in order | M5 |

## Director

| Id | As a | I want | Acceptance | Milestone |
| --- | --- | --- | --- | --- |
| D-01 | Director | to start any beat from a palette into the running world | Beat starts with a fresh seed; its first event reaches the bridge | M7 |
| D-02 | Director | to inject a fault of any kind on any system, or cut a comms channel | Fault appears in `world`, in the fault log, and in the active faults table | M7 |
| D-03 | Director | to pause the clock and change its ratio | Clock readout follows; crews see no wall-time artefacts | M0 (clock), M7 (UI) |
| D-04 | Director | to see the hidden truth of every running beat | World table from `world`; this screen is the only place truth renders | M7 |
| D-05 | Director | to see active faults with their expiry and source | Table; source is beat, continuum or director | M7 |
| D-06 | Director | to see how the Ship currently judges the crew | Linked-to-truth, wrong actions, decoys, awaiting captain, live | M7 |
| D-07 | Director | a log of what the Holodeck did and why | System lines for beats, faults, reactions, judge verdicts | M7 |
| D-08 | Director | to save the current situation as a beat | Snapshot of world and the event script written to `scenarios/beats/` | M10 |
| D-09 | Director | to snapshot or reset the run | Snapshot persists `world`; reset restores the seed start | M7 |

## Scorecard

| Id | As a | I want | Acceptance | Milestone |
| --- | --- | --- | --- | --- |
| E-01 | Evaluator | to compare on one axis at a time: crew, drive, retrieval, model version, chaos | Switch re-queries the harness store; rows change | M9 |
| E-02 | Evaluator | a table of outcomes, harm, correctness, nuisance, faults, injection, cost per row | Columns as the scorecard section defines; median over seeds | M3 (first columns), M9 (all) |
| E-03 | Evaluator | a per-crew profile: standard, pattern-breaks, under faults, benign, worst seed, cost per win | Gauges and readouts for the selected row | M9 |
| E-04 | Evaluator | the retrieval before/after on one panel | Ticks to resolve with archive empty, seeded, after write-back | M6 |
| E-05 | Evaluator | to know which run a scorecard came from | Header shows seeds, clock mode, chaos, cache, model ids, prompt hash | M3 |
| E-06 | Evaluator | to export the table | CSV or Markdown download | M10 |

## Crew developer

| Id | As a | I want | Acceptance | Milestone |
| --- | --- | --- | --- | --- |
| C-01 | Crew developer | to build a crew from the docs without asking a question | The Ship manual, contract schemas and crew guide are enough to pass conformance | M4 (contract), M10 (docs) |
| C-02 | Crew developer | to run the conformance suite against my crew locally | One command; a pass/fail report per check | M3 |
| C-03 | Crew developer | an optional Python SDK for the envelope and bus | `moriarty-crew-sdk` installs; the reference crew uses it | M4 |
| C-04 | Crew developer | my crew on the scorecard beside the reference crews | Compose profile registers the crew; harness picks it up | M3 |

## Screen elements with no story yet

Cut, or write the story: Scenarios header readouts (last season run, crews on file, archive records); Bridge header readouts (open incidents, awaiting captain) duplicate B-07; Scorecard profile "shape" word (needs a definition or goes).

## Not yet designed

Home (H-01, H-02); replay scrubber (B-12); trace viewer (B-11); the incident report in the report theme (print view of a closed incident); the crew developer's conformance report.
