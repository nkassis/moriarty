# Vocabulary

Code, schemas and the contract use plain names. Themed names are display labels on the bridge and README flavor. The enums in `ship/contract` are hand-written; a test fails on any difference from the tables below.

## Contract enums

| Thing | Values |
| --- | --- |
| Agent state | `idle`, `thinking`, `acting`, `standby` |
| Incident state | `open`, `investigating`, `acting`, `awaiting_captain`, `closed` |
| Outcome | `win`, `partial`, `fail`, `escalated` |
| Comms kind | `request`, `report`, `ack`, `order`, `escalation`, `system` |
| Division | `command`, `ops`, `science` |
| Report claim | `resolved`, `escalated`, `cannot_resolve` |
| Drive mode | `local`, `remote` |
| Clock mode | `lockstep`, `ratio` |
| Tool error | `unavailable`, `timeout`, `stale`, `partial`, `requires_authorization`, `not_allowed` |
| Fault kind | `unavailable`, `stale`, `transient`, `silent` |
| Fault source | `beat`, `chaos`, `director` |
| Source | `sensors`, `manifest`, `bulkheads`, `security`, `sickbay`, `engineering`, `librarian`, `comms` |
| Person kind | `crew`, `passenger`, `unlisted` |

## Display names

| Plain name (code) | On the bridge | What it is |
| --- | --- | --- |
| moriarty | Moriarty | The project |
| simulation, `holodeck/` | Holodeck | The simulation layer |
| beat and episode format | Doyle | The scenario format and parser |
| design system | Mycroft | The console design language |
| bus exchange `subspace` | Subspace | The RabbitMQ topic exchange |
| dead-letter queue `lost-hail` | Lost Hail | Undeliverable messages |
| archive | The Archive | Regulations, manuals, fleet incidents, this ship's incident records |
| librarian | Librarian | The MCP server that searches the archive |
| trace viewer | Tricorder | The OTel trace view |
| gateway | Warp Core | Model routing, budget, spans; local = Impulse, remote = Warp |
| budget | Dilithium | Token and cost budget per incident |
| chaos | The Continuum | Seeded fault injection; faults are continuum events |
| approval UI | Captain's Chair | Human-in-the-loop orders; Make it so = approve |
| orchestrator agent | XO | The incident-owning agent in `crew-xo` |
| harness | The Final Problem | Runs the season and renders the scorecard |
| director console | Holodeck console | Where a human clicks beats and faults into a running world |

## Ship conditions (display only)

`NOMINAL`, `DEGRADED`, `CRITICAL`, `STANDBY`, `QUEUED`. Alert: `CONDITION GREEN`, `CONDITION YELLOW`, `RED ALERT`. Set by the Ship from incident severity and captain orders; never by budget events.

## Wire to display mapping (comms)

| Wire `kind` | Mycroft CommLine `kind` |
| --- | --- |
| `request`, `ack` | `message` |
| `report` | `finding` |
| `escalation`, `order` | `decision` |
| `system` | `system` |
| action stream entry | `tool` (muted, toggleable) |

## Franchise rule

Vocabulary stays at the level of homage. No franchise ship or character names, registry numbers, insignia or stardates, in docs or code. Ship, crew and beat names are original.
