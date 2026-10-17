# Independent review: Moriarty architecture bundle

Reviewer stance: principal engineer who has run multi-agent LLM systems in production and sits on senior/architecture hiring panels. I saw only the six files in the bundle. File references use the bundle names; section references use the headings in `02-moriarty-architecture.md` (the "doc") unless stated otherwise. The bridge screen is `03-bridge-screen.dc.html` (the "screen"); the design system is `04-mycroft-design-system-README.md` and `05-mycroft-tokens.json` ("Mycroft").

Short version before the detail: this is a genuinely above-average architecture document. It makes real decisions (Ship-judged outcomes, held-out seeds, rules baseline first, network boundary as the interface, gateway as the enforcement point, output protocol with a stated reason) and it is honest about what is open. A panel would engage with it seriously. It also has one unmade decision that undermines its central evidence claim (clock/tick semantics), one undefined interface that the whole thing stands on (Holodeck to Ship), an enforcement story that will not hold on the platforms named, and a vocabulary that has drifted apart across doc, screen and design system. None of these are fatal; all of them are the kind of thing a skeptical panel will find in the first fifteen minutes, so they should be fixed before the project is shown.

---

## 1. Brief coverage

### Requirements and constraints (01-brief.md, items 1 to 10)

**1. Standard technologies (Python; React + Vite + TanStack; Postgres/pgvector; RabbitMQ; LangChain; Ollama; cheap remote LLM acceptable; output-token protocol).**
Coverage: **fully.**
Where: "Tech stack and repo layout" (table), "LLM strategy" (Drive modes, Output protocol, Cost controls, Warp Core), "The Archive and the Librarian" (pgvector + tsvector).
Judgment: every named technology is present and each has a role; the output protocol has a reason attached ("models mirror the verbosity they are fed"), which is the kind of detail that distinguishes experience from a checklist. The remote model names (Haiku 5.5, Qwen 3.7 Flash, DeepSeek V4 Flash) and the "5x above 100K tokens" pricing claim read as placeholders the doc itself says to verify; the panel will ask what was actually run.

**2. RAG component: a library and a ship's computer (Data analogue) an agent interrogates, including research of prior events.**
Coverage: **partly.**
Where: "The Archive and the Librarian" (four collections, hybrid search, Librarian tools, Science station, write-back, retrieval evals); "Something in the Water" sketch in "Holodeck and episodes"; `archive_seed`.
Judgment: the library half is well designed and the before/after write-back demo is a strong idea. The "ship's computer" half is not designed: the Librarian is a search API (`search_archive`, `get_record`, `similar_incidents`), not an entity an agent interrogates conversationally, and the doc never says whether that collapse is deliberate. Mycroft meanwhile calls Science "the library-and-computer agent", which puts the computer in the Crew layer; the doc puts the Librarian in the Ship layer. The brief's Data analogue therefore has no settled home. Say explicitly: "the ship's computer is the Librarian MCP server plus the Science station's research workflow; there is no separate reasoning computer", or design one.

**3. A comm channel the human can watch.**
Coverage: **fully.**
Where: "Comms channel" (envelope, example, click-through to trace, captain participation, replay, restraint); "Bridge UI" Comms panel; screen Comms frame.
Judgment: well covered and the "if it is not on comms, it did not happen" rule is a real architectural commitment. The screen does not follow the doc's own restraint rule (tool calls on the main channel) and the envelope is missing fields needed for request/reply; see sections 2 and 4.

**4. Ship/Crew separation so the project is a playground; episodes as multi-event stories.**
Coverage: **fully** as intent; **partly** as enforceable design.
Where: "Three layers", "The Ship contract", "Crew" ("Why no code interface"), "Holodeck and episodes" (acts, interleaving).
Judgment: the Ship/Crew boundary is the best-designed thing in the document. The Holodeck/Ship boundary is asserted in the layer table but never specified: how hidden truth reaches the mocked sensors, how MCP action calls reach Doyle `reactions`, and where system state lives are all undefined (section 4). The brief asks for separation between simulation and ship; the doc delivers separation between ship and crew.

**5. Project name Moriarty; themed names welcome.**
Coverage: **fully.**
Where: "Pitch", "Glossary of themed names".
Judgment: names are consistent and the public-domain reasoning (Conan Doyle, The Final Problem, Doyle format) is sound. Some themed names collide with each other (Red Alert, Ship's Log; section 2).

**6. Crew not bound to a code interface; any library or tech can build a crew.**
Coverage: **fully.**
Where: "Crew" ("Why no code interface", "What the Ship provides instead", conformance suite, optional SDK "after the second crew exists").
Judgment: this is the strongest section. The wire-as-interface decision is argued, the conformance suite is the right enforcement instrument, and "two implementations make a contract real; one makes a guess" is exactly what a panel wants to hear. Gap: the doc claims the crew container "receives exactly a bus URL and the MCP endpoints" while also requiring LangGraph checkpointing and allowing crew-private Redis/tables; the claim needs to be "no Ship credentials".

**7. Local running: compose and/or Docker Desktop kind Kubernetes, Kubernetes preferred; host-level LLM via a proxy.**
Coverage: **fully** as plan; several claims will not survive the platforms named.
Where: "Running it locally" (compose inner loop, Kubernetes deployment story, KEDA, operators, OTel DaemonSet, NetworkPolicy, model on host), "Warp Core" (proxy).
Judgment: compose-for-inner-loop, k8s-for-deployment is the right split and the reason given (prompt iteration hundreds of times) is correct. But: kind's default CNI and Docker Desktop's Kubernetes do not enforce NetworkPolicy, so "a crew namespace may reach the bus, the MCP services, and the gateway, nothing else" is not true without installing Calico or Cilium; `host.docker.internal` is not reliably resolvable from pods inside a kind node without a Service/Endpoints or hostAliases; CloudNativePG's stock images do not ship pgvector. Details in section 4.

**8. Randomness in what the ship sees, so evaluation detects overfitting.**
Coverage: **fully** in intent; **partly** in mechanism.
Where: "Randomness, so crews cannot overfit" (surface / structural / causal), `params` and `sensors` sketch, "Seeds and distributions" in Evals (tuning vs held-out, pattern-break column).
Judgment: three layers of seeded randomness plus a held-out seed split plus pattern-break episodes tracked separately is a mature answer, better than most production eval setups. The mechanism is undermined by the determinism claim ("same pair always produces the same world"): the world trajectory depends on crew actions, and crew actions depend on model latency if ticks are wall-clock. See section 4, finding on clock semantics.

**9. Architecture doc should become spec.md; a Claude Design screen on the Mycroft design system should let the human watch; judge the screen on information design.**
Coverage: **partly.**
Where: the whole doc; the screen; "Bridge UI" panels and design rules.
Judgment: the doc is an architecture narrative, not a spec; the distance is substantial (section 7). The screen exists and is built on the design system's components, and most of what it shows maps to a doc panel. Its information design has real problems for following an incident (no incident id per line, lines out of time order, tool calls inline, an XO in a choreography crew, fixture timestamps in the future); section 5b.

**10. Keep clear of Paramount IP: homage-level vocabulary; no franchise names, ship names, registry numbers, insignia, stardates.**
Coverage: **mostly**, with three violations of the maker's own rule.
Where: "Goals and non-goals" (non-goal), "Glossary", Mycroft "Keeping clear of the franchise".
Judgment: (a) The event schema has a field literally named `stardate` whose note says "never a stardate" ("The Ship contract", Events table). Rename it `ship_time` or `t`. (b) "LLM strategy", Output protocol: "Starfleet-style comms are clipped, and that is the style guide." Starfleet is a franchise name, excluded by the brief. (c) "Glossary", Station states row: "in the Jefferies tube = errored" is a franchise-specific term named after a real production designer, not generic sci-fi. "Make It So" (Captain's Chair row, screen button) is a catchphrase; borderline, probably fine as homage, but it is the kind of thing a cautious reviewer flags. The rest (holodeck, tricorder, turbolift, dilithium, warp, red alert, tetryon) sits at the "widely used" level the brief allows.

### "What to judge" bullets

**Does the architecture credibly demonstrate agentic-systems design skill to a skeptical senior audience?**
**Partly, leaning yes.** The decisions that carry the demonstration are present and argued: environment judges outcomes against hidden truth, no-LLM baseline first, held-out seeds, pattern-break episodes, retrieval verified before use, budget caps that escalate instead of silently stopping, gateway as the single accounting point, structured output with a reason. What weakens it: the eval evidence claim rests on an undefined clock; failure handling (redelivery to action idempotency, stuck interrupts, concurrent station replicas, judging races, archive poisoning) is mentioned at the level of "crews must tolerate redelivery" and not designed; and the parts of the system where multi-agent systems actually fail (what a station sees per turn, how context is bounded, how an agent waits for another agent's reply) are deferred to one open decision ("Interrupt transport"). Section 3.

**Is the Ship/Crew/Holodeck separation real and enforceable?**
**Ship/Crew: real, enforceable with work the doc has not named** (RabbitMQ topic permissions, compose network segmentation, a CNI that enforces policy). **Holodeck/Ship: asserted, not designed.** The Holodeck must write truth into the systems the Crew reads and must observe the Crew's action calls, and neither path is specified. Also, captain approval before consequential actions is Crew-side policy (LangGraph interrupts), so the Ship cannot tell whether a crew skipped it; that makes "escalations warranted" unscorable from the Ship's side. Sections 3 and 4.

**Is the plan buildable by one person part-time over a couple of months, and is the build order right?**
**Steps 1 to 6: plausible but tight. Steps 7 to 11: not in two months.** The order is mostly right (vertical slice, judge before UI, second crew before SDK). Two things are in the wrong place: the gateway is deferred to step 10 but is the only cost/budget/trace point from step 2 on; the simulated clock is never scheduled and must be in step 1. Section 6.

**Does the document hang together: terminology, schemas, names, states consistent across sections and with the design system?**
**Partly.** Within the doc: mostly, with a handful of real contradictions (incident assignment vs crew linking; "exactly a bus URL" vs crew-private DB; Ship "never touches which crew is running" vs heartbeat registration; file_report with no transport; Sensors as both system and station). Across doc, screen and Mycroft: three separate vocabularies for comm kinds, incident states and conditions; XO on a choreography bridge; time inconsistencies in the screen fixture. Section 2.

**What is missing that a reviewer would ask about?**
Clock semantics; Holodeck-Ship interface; incident assignment; approval enforcement and a scripted captain for unattended evals; what a station sees per turn and how context is bounded; message loop prevention in choreography; action idempotency; station-replica concurrency; outcome judging timing and the failed-report path; envelope correlation fields; scorecard metric definitions; Doyle blocks the scorecard references but the format does not have; archive write-back trust; alert condition source; adversarial content (tool results that look like instructions) as a pattern-break axis; wall-time and cost budget for the season. Sections 3, 4, 7.

**How far is this document from a spec, and what would get it there?**
Far. It is a good architecture narrative with one schema sketch (Doyle) and two field tables (event, envelope). A coding agent would stop with questions on the first hour of step 1 (clock), step 2 (tool signatures, system state), step 3 (judge algorithm, report transport). Section 7 lists what is missing.

---

## 2. Internal consistency

Each item: what conflicts, where.

### Within the architecture doc

1. **Incident assignment vs crew linking (core eval claim).** "The Ship contract", Events table: `incident_id` is on every inbound event ("Groups events into an incident; also the comms channel name"). "Holodeck and episodes", Interleaving: "Whether a crew spawns a second incident or assumes a connection is where coordination architectures get tested for real." If the Ship/Holodeck stamps incident ids on events, the crew never decides whether two events are one incident; the test the doc says is the point of interleaving cannot happen. The screen follows the first reading (INC-0042 and INC-0043 are pre-assigned). One of the two must go.

2. **`file_report` has no transport.** "The Ship contract" 4 (Outcomes): "A crew may `file_report` claiming resolution." "Crew", Rules: "a final `file_report` with a fixed schema." "LLM strategy", Output protocol: same. Conformance: "files a report." But `file_report` is not in any MCP system's tool table ("The Ship contract" 2), not in the envelope `kind` enum ("Comms channel"), and the only Ship-side incident system ("Incident Desk" with `claim_step`) appears solely in "Open decisions". Meanwhile `file_record` on the Librarian is a different operation (write-back after close). The two names are close enough that a reader assumes they are one thing.

3. **"Exactly a bus URL and the MCP endpoints" vs crew-private storage.** "Three layers", Enforced physically: "The crew container receives exactly a bus URL and the MCP endpoints: no database credentials." "Crew", Rules: "Private memory (Redis, tables) is the crew's to bring." "Crew", Bridge stations: "each station is a LangGraph graph with explicit state, checkpointing, and interrupts." "Open decisions", Interrupt transport: "Checkpointer in Postgres." A LangGraph crew with a Postgres checkpointer holds database credentials. The claim should be "no Ship credentials".

4. **Ship "never touches which crew is running" vs heartbeat registration.** "Three layers" table, Ship row, Never touches: "Which crew is running, how it coordinates." "Crew", What the Ship provides: heartbeat "so the Ship and the Stations panel know who is on the bridge. This is registration." The Ship knows the crew name and every station's state. The table cell is wrong as written.

5. **Sensors: system or station?** "The Ship contract" 2: Internal Sensors is an MCP system. "LLM strategy", Per-station routing: "high-volume triage stations (Ops, Sensors, Medical, Engineering)". The station table in "Crew" has no Sensors station. Mycroft's `crew-science` usage string says science covers "sensors analysis" while the doc gives Sensors tools to Ops (gold).

6. **Outcome enum.** Doyle `resolution` has `win / partial / fail`. Evals scorecard: "Outcome (win / partial / fail / escalated)". "Three layers": "The Ship ... declares an incident resolved." "Holodeck and episodes": "An episode can end 'resolved, badly.'" Is `escalated` a terminal outcome (the no-good-outcome episode says escalation is the correct answer, so presumably yes), and how does Doyle express "escalated is the win"? The sketch cannot.

7. **"Red Alert" means two things.** "Glossary": "Red Alert: Budget or cap exceeded; automatic escalation." "Bridge UI": "Four themes: standard, yellow alert, red alert" with "alerts are the AlertBanner switching the theme"; Mycroft: "RED ALERT" is a ship alert condition. The screen's red/yellow banner is about the intruder and contagion, not budget. Either rename the budget event (the doc already has "dilithium reserves") or accept that the console's RED ALERT will fire for token overruns.

8. **"Ship's Log" means three things.** "Glossary": "Ship's Log: The event and audit tables." "The Archive" collections table: "This ship's log: Written by the crew at incident close" (a retrievable collection). Screen Incidents table caption: "Ship's log" (the incident list). "Comms channel", Replay: "Everything is persisted in the ship's log." Pick one; suggest "Ship's Log" = audit tables, "Incident Records" = the crew-written archive collection.

9. **"Manifest" means two things.** "Glossary": "Manifest: Ship state (people, sections, systems)." "The Ship contract" 2: Manifest is the people system (`lookup_person`, `list_section_occupants`, `flag_person`); sections are under Turbolift and Bulkheads, systems under Engineering.

10. **Station naming.** "Crew" table: "Tactical/Security". Comms example and screen: "SECURITY"/"Security". Pick one.

11. **Envelope addressing.** "Comms channel" envelope: `to` is "a station, `bridge`, `captain`, or `all-hands`". Example: "CAPTAIN → ALL". The example uses a value the enum does not have.

12. **Orders as "events".** "The Ship contract" 3: "Captain's orders arrive to the crew the same way, as events of kind `order`." "Comms channel": orders are envelope messages with `kind: order` on the comms channel. Crews bind `alert.<domain>.*` for events ("Crew" table); the routing key for comms messages is never given beyond `comms.#`, so how a station receives an order is unspecified. The doc says "events" in one place and "comms" in another for the same message.

13. **Gateway timing.** "LLM strategy", Warp Core: "every crew is told to use" the gateway; it owns cost accounting, budget enforcement, model-call spans, fair comparison. "Build order" step 10: "Warp mode and the model comparison. Remote model routing..." and "Decide at step 10" for build vs buy. Steps 2 to 9 produce scorecards with "tokens, cost" columns (Evals table, source: OTel spans) and "Token usage and estimated cost logged per agent run in the audit table" (Cost controls), but the component that produces those numbers is not built until step 10, and crews are not supposed to hold provider keys or self-report.

14. **Tool calls on the channel.** "Comms channel", Restraint: "Tool calls stay off the main channel... Those show in a muted 'internal' layer that can be toggled on." Screen Comms frame: `kind="tool"` lines inline with findings and decisions, no toggle shown. The doc's own panel table says "internal layer toggle".

15. **Hidden state on the bridge.** "Bridge UI", Design rules: "Nothing on the bridge reveals Holodeck hidden state." "Bridge UI", Panels, Incidents: "Open incidents with state, act, elapsed." The act number is the Holodeck script's structure; showing "Act 3" tells the human the episode escalated before the crew knows. The screen shows an Act column (2, 2, 3).

16. **Determinism vs wall clock.** "Holodeck and episodes", Determinism: "Same seed, same crew, same tick schedule gives the same hidden-state trajectory." "Evals", Two kinds of run: "gateway response cache on, temperature 0, so reruns are deterministic." "LLM strategy", Known constraints: "Five stations reacting to one event will queue." If ticks are wall-clock, queueing changes when actions land, which changes the trajectory; the two sections cannot both be true unless the clock is simulated, which is never stated.

17. **Scorecard references Doyle blocks that do not exist.** "Evals" table: "Correct actions taken: Episode's expected-action list"; "Escalations ... vs. episode rules"; "Red herrings chased: Tool calls against the decoy". The Doyle sketch has no `expected_actions`, no escalation rules, and `red_herring: true` is on an act with no definition of which tool calls count as chasing it.

18. **Conformance suite location.** "Crew": "A conformance suite: a container." "Tech stack", repo layout: "`ship/contract` holds schemas and the conformance suite." `evals/` holds "The Final Problem harness, retrieval evals". Where the conformance container's code lives is ambiguous between `ship/contract` and `evals/`.

19. **Compose non-goal vs Kubernetes production patterns.** "Goals and non-goals": "Production hardening (auth, multi-tenancy, HA). Single-user, docker compose up." "Running it locally": RabbitMQ cluster operator, CloudNativePG, KEDA, NetworkPolicy, "the production way". Not a contradiction exactly, but the scope of the k8s section is at odds with the stated non-goal and with a two-month plan.

20. **Heartbeat schema vs Stations panel.** "Crew": heartbeat carries name, index, division, state, current activity. "Glossary", Station states: heartbeat "may carry a `detail`". "Bridge UI", Stations panel: "name and index on a division chip, state word, Cascade, current activity". The screen also shows `role`, a tool-call count and a last-activity time per station; the heartbeat does not carry them (see 5b).

### Between the doc and the screen

21. **XO on a choreography bridge.** Screen header: "crew choreography · impulse drive". Screen Crew frame: an XO card, "Command · incident owner", state thinking; XO lines on comms; the pending escalation is from "XO 01". Doc "Crew" table: "XO (orchestrator crews only)". Doc coordination model 2: "`crew-choreography`... No central brain." The screen depicts crew-xo and labels it choreography.

22. **Incident state words.** Doc: `open, investigating, acting, awaiting_captain, closed`. Screen Incidents table Condition column: "Acting", "Investigating", "Resolved". "Resolved" is not a state; INC-0042 shows "Acting" at 00:04:12 although the XO escalated to the captain at 00:04:11 (should be `awaiting_captain`). Mycroft's fixed condition words (`NOMINAL / DEGRADED / CRITICAL / STANDBY / QUEUED`) are a third vocabulary the Status pill is supposed to carry.

23. **Comm kinds.** Doc envelope `kind`: `hail, request, report, ack, order, escalation`. Mycroft CommLine `kind`: `message, tool, finding, decision, system`. Screen uses `system, tool, finding, decision`. The XO's escalation is rendered as `decision`; the captain's order as `decision`. There is no mapping from the wire enum to the display enum anywhere.

24. **Comms style.** Doc, Output protocol: "Tool calls are the only output... No narration." Doc example lines are telegraphic ("Intruder, deck 7 sec 12, one lifeform, unarmed. Request team."). Mycroft, Voice: "Agents speak in first person in CommLine: 'I am checking the deck 7 sensor log.'" Screen: "I am checking the manifest against internal sensors for deck 7 section 12." That line is narration the doc says agents never emit, and at ~150 characters the XO line would likely exceed a "hard character cap" the doc never sets.

25. **Time inconsistencies in the fixture.** Screen header "Ship time 00:04:12". INC-0041 timeline: resolved at 00:08:40, Engineering card "last message 00:08:40": four and a half minutes in the future. INC-0042 row "Elapsed 00:01:06" but its first event is at 00:03:58, so elapsed should be 00:00:14. INC-0043 "Elapsed 00:04:12" matches a 00:00:00 open. Medical's channel line is stamped 00:04:03 but appears after Security's 00:04:06 line. Also, with two interleaved episodes, the doc's "simulation seconds from episode start" has no single origin; the screen assumes one ship clock, which is right, but the doc does not say it.

26. **Dilithium semantics.** Doc Glossary: "Dilithium: Token and cost budget per incident." Screen header: "Dilithium 59 %" (whose budget?), gauges INC-0042 31 %, INC-0043 58 %, "Hour 22 %", with warn at 0.7 and crit at 0.9 (so these are fraction consumed). The header 59 % is neither the max nor the sum of the incident gauges and is unlabelled as consumed vs remaining.

27. **Alert condition source.** Screen: AlertBanner yellow with detail "Intruder on deck 7 · contagion spreading on the same deck · two incidents open." Nothing in the contract, the Ship API or the Holodeck section says who decides the bridge alert condition (event severity? the captain? incident count?).

28. **Sender "Sensors" on comms.** Screen: first CommLine from "Sensors", kind system. Doc envelope `from` is "station name"; Sensors is a Ship system. Acceptable if events are rendered into the channel as system lines, but the doc says the Comms panel is backed by the `comms.#` tap only and the "event stream" is a separate subscription.

### Between the doc and Mycroft

29. **Where the ship's computer lives.** Mycroft Principles and `crew-science` usage: "the library-and-computer agent" is a Crew member in teal. Doc: the Librarian is a Ship MCP server (pastel); Science is the Crew station that calls it. The screen's Science card says "Sciences · library and computer". The layer boundary for the brief's Data analogue is drawn differently in the two documents.

30. **Standby.** Doc station states `idle / thinking / acting / standby`; Mycroft conditions include `STANDBY` as a Ship condition and Cascade "holds still when idle" with no mention of standby. Same word, two meanings, documented in the glossary but still a trap for the UI.

31. **Division names.** Doc heartbeat division `command | ops | science`. Mycroft tone props: `command | ops | science`. Consistent. Screen role captions use "Operations" and "Sciences" (plural) while the station table uses "Science". Minor.

32. **Status tokens missing a theme.** `05-mycroft-tokens.json`: `status-ok`, `status-warn`, `status-crit` define `standard`, `red-alert`, `report` and omit `yellow-alert`; `crew-*` tokens omit both alert themes but their usage text says they are identical across console themes. The status tokens' usage text does not say that. Not under review, but it will bite the screen's yellow-alert default.

33. **Voice rule vs doc style guide.** Mycroft: "No emoji, no exclamation marks, no sentence case on a band", "Agents speak in first person". Doc: "Starfleet-style comms are clipped, and that is the style guide." Two style guides for the same text, one of which uses a franchise name.

---

## 3. Domain judgment

### Does it answer the question asked?

Mostly. The question is "can this person design agentic systems well", and the doc's answer is "an environment that judges agents against hidden truth, a wire contract any crew can target, and a harness that compares them on held-out seeds". That is the right answer and it is a better answer than "look at my LangGraph graph". The doc also shows production scars in the right places: verbose tool output trains verbosity; caps escalate rather than silently stop; a scorecard with variance separates measurement from anecdote; the rules baseline exists to be beaten; pattern-break episodes exist because ten identical log records will make retrieval confidently wrong.

What the panel will push on:

**The harness is the deliverable, and the doc does not quite say so.** On scripted episodes with a known tool API, `crew-rules` will very likely beat the LLM crews on the standard set, and the LLM crews' only defensible advantage is on pattern-break and causal variants. The doc should state this expectation up front: "rules wins the standard set, loses the pattern-breaks; that gap is the measurement". If the maker does not say it, the panel will say it as a gotcha. If the LLM crews lose everywhere, the project still demonstrates something (the harness found it), but only if the doc framed it that way first.

**"Where does it fail?" is answered thinly.** The doc names Ollama serialization and small-model tool-use inconsistency. A panel of people who have run these systems will ask about: a station that reacts to another station's `report` with a `report` (comms loops in choreography); a station replica that picks up the second event of an incident while the first replica is mid-run on it (duplicate dispatches); a redelivered event after a crash mid-tool-call (the seal is idempotent, the dispatch is not); an interrupt waiting for a captain who is a harness, not a human; a report filed one tick before the hidden state flips. None of these are designed. "Max tool iterations" and "event_id dedupe" are the only failure controls in the Crew rules.

**The central comparison has a confound.** Local vs remote on the same crew is sold as an architecture comparison ("the scorecard shows the difference"). If the Holodeck tick is wall-clock, a 3-second local model and a 400 ms remote model face different worlds (more spread, intruder further along) before they act. The scorecard would measure latency, not model quality. This is the first thing I would ask, and the doc has no answer. Section 4, clock.

**Context management is absent.** What does a station see on each turn? Its bound events, plus which comms (addressed to it, to bridge, to all-hands, all of the incident channel)? How is the per-turn prompt built; does history grow with every comms line on the incident? "Max context per incident" is a cap, not a design. For a multi-agent system this is the question that determines whether it works on a 7B model at all.

**Approval is unenforced.** "Interrupts for captain approval before consequential actions" is LangGraph behavior inside the crew. The Ship cannot tell whether a crew sealed a deck without asking; so "Escalations to captain (and whether warranted)" in the scorecard is a measurement of the crew's self-reported behavior, and a crew that never asks and always seals looks fast and decisive. The boundary the doc is proud of has a hole exactly where human-in-the-loop lives.

**The doc separates Ship from Crew and forgets to separate Holodeck from Ship.** Everything that happens between "hidden state" and "what sensors report" is one sentence ("Visible only through sensors, which are partial and sometimes noisy"). The `sensors:` noise block in Doyle implies the Holodeck defines noise; the Sensors MCP server must apply it; so the Ship reads episode config. The `reactions.on: {tool: seal_section}` block implies the Holodeck observes MCP calls; nothing says how. This interface is where the "playground" promise is kept or broken, and it is undesigned.

### Overclaimed

- "the same pair always produces the same world" (Randomness) and "reruns are deterministic" (Evals). True only with a simulated clock, byte-identical prompts (no timestamps, stable tool-result ordering, stable retrieval tie-breaks) and a response cache keyed on the full request body including tool schemas and history. Say "reproducible to the extent the crew's inputs are identical" and list the conditions.
- "Enforced physically... If a crew cannot cheat, the contract stays real." On the named platforms it is enforced by convention until RabbitMQ topic permissions and network segmentation are configured, and the k8s NetworkPolicy claim is false on kind/Docker Desktop defaults.
- "Cost per episode ... on the order of a cent." No arithmetic. A rough count (5 stations × 8 turns × 3K input + 150 output) is 120K input tokens; at cheap-flash pricing that is about a cent, at Haiku-class pricing it is 5 to 15 cents before caching. Show the estimate.
- "Idle bridge, zero pods; three alerts land, Ops scales out." In Impulse mode Ollama is the bottleneck, so scaling Ops to N pods just makes N pods wait at the gateway. KEDA here is demo-ware unless the doc says it is for Warp mode.
- "Retrieval that provably changes outcomes." The before/after design is good, but "provably" on 20 seeds with an LLM crew is "measurably with confidence intervals". The Evals section itself says "report variance"; the Goals section should match.

### Underclaimed

- The eval design (tuning/held-out split, pattern-break column, median and worst-case, two kinds of run) is stronger than most of what I have seen in production agent teams and the doc buries it in the Evals section. The Pitch should lead with it.
- The output protocol's reasoning and the "Tool results are short... models mirror verbosity" observation are hard-won; they should be called out as such in the README.
- The conformance suite as the definition of "a crew" is the single best enforceability idea and is mentioned in one bullet.

### Decisions stated without a reason, or with a weak one

- "Hybrid search ... RRF": reason given, good. "nomic-embed-text or a bge model": no reason, no dimension noted.
- "RabbitMQ": no reason vs Redis Streams/NATS; the brief allows "or similar". One sentence would do (topic routing by domain, per-crew queues, DLQ, management UI for the demo).
- "One trace per incident rooted at the Holodeck event": no reason given for one trace vs one trace per run with links; and the long-running-root-span problem is not acknowledged.
- "Jaeger default": reason given (simplest), fine.
- "LangGraph for reference crews": "state, checkpointing, interrupts" is a reason. Fine.
- "Compose profile selects the crew": fine.
- "Incident state machine in the Ship" for choreography: the leaning is "a `claim_step` tool ... so the state is auditable" but the panel will ask: if the Ship defines the step list per incident, the Ship encodes the solution path and leaks Holodeck knowledge into the environment. What is a "step"? Who authors them? This is a real design tension and the doc does not see it.
- "Embeddings stay on Ollama in both modes": stated, not reasoned (presumably: index stability, cost). Say it.
- "KEDA ... each station is a Deployment scaled 0 to N": no reason that survives Impulse mode; and no treatment of what happens to a station waiting on an interrupt when its pod is scaled to zero.
- "Tool results are short and structured: five fields that matter": good reason. Keep.
- Five-station crew with "cheap" tier for four stations: no evidence yet; that is fine as a hypothesis if labelled one.

### Generic content

Most of the doc is specific. The parts that read as a tool list rather than decisions: the Kubernetes bullets ("Operators over hand-rolled StatefulSets", "Tilt or Skaffold if..."), the Observability backend paragraph, and "Prompt caching on system prompts and tool schemas". The Bridge UI panels table is fine as inventory. The Glossary is themed flavor; harmless but it is where the IP slips are.

---

## 4. Technical judgment

### A. Clock and tick semantics (highest severity)

The doc says "tick loop", "ship-seconds", "elapsed >= 90", "Time to resolution (ship time)", "Holodeck clock", and never defines the relationship between simulation time and wall time. Consequences:

- **Fairness.** If ticks advance on wall time, model latency changes the episode. Local vs remote and cheap vs strong comparisons are confounded by speed. Ollama queueing across five stations (which the doc acknowledges) makes the Impulse crew face a harder episode than the Warp crew.
- **Eval wall time.** 5 episodes × 20 seeds × 3 crews × 2 drive modes × 2 retrieval states = 1200 runs. At 1x wall clock with a 600-ship-second fail timeout, a full season is days. The "runs are cheap enough to repeat" claim only holds if ship time can run faster than wall time.
- **Reproducibility.** "Same seed, same tick schedule" names the dependency without resolving it.
- **Captain waits.** If the clock runs while an interrupt waits for a human, the contagion spreads while the captain reads. That may be intended, but then "Captain interrupts (time waiting for a human)" in the trace is also lost ship time and must be accounted for in the scorecard.

What to decide: a Ship-owned logical clock. Options: (a) lockstep: the Holodeck advances one tick when every station has reported idle or a tick budget expires; (b) fixed ratio with pause: ship time runs at k× wall time, paused during `awaiting_captain`; (c) discrete-event: the Holodeck advances to the next scheduled trigger when the crew is quiescent. Option (a) or (c) makes evals fast and fair and makes determinism real; option (b) is simplest and keeps the live demo feeling live. Either way, `ship_time` must be stamped by the Ship on every event and envelope, and model latency should be its own scorecard column.

### B. The Holodeck to Ship interface (undefined)

Needed and not present:

- **Where system state lives.** "Mocked but stateful" MCP servers plus "the Holodeck reads their state to judge outcomes" implies shared storage. If each FastMCP process keeps state in memory, the judge cannot read it and a restart loses it. Decide: Ship Postgres schema `world` (truth, Holodeck-writable) and `observable` (what systems return), or systems that compute observations from truth on demand with noise applied per the episode's `sensors:` block.
- **How truth reaches sensors.** `lifeform_count(deck 7)` must return manifest count + intruder (+ noise). Who computes that? Define: systems read truth through an internal Ship-only API or table, never exposed on the crew network.
- **How actions reach reactions.** `reactions.on: {tool: seal_section, deck: 7}` requires the Holodeck to see every action tool call. Define an internal `action.<system>.<tool>` topic the systems publish on every action call (with `event_id`/`incident_id`/`station`/args), consumed by the Holodeck and by the scorecard ("Correct actions taken", "Wrong or harmful actions", "Red herrings chased" all need this stream). This also gives the Ship the audit it needs to enforce approvals (see D).
- **Who seeds the Manifest.** `params.intruder: {sample: manifest.non_crew}` needs passengers with names, decks and sections generated per seed and written into the Manifest system before the first event. Holodeck writes, Ship system reads: same interface.
- **Event relay.** "Published by the Holodeck through the Ship": does the Ship stamp `incident_id`, `event_id`, `ship_time`, `trace_id`, and validate against the contract schema before publishing on `subspace`? Say so; it is where contract enforcement on the inbound side lives.

### C. Message bus: redelivery, idempotency, concurrency, loops

- **Acks and prefetch.** A LangGraph run takes seconds to minutes. If the station acks after the run, a crash mid-run redelivers and the run restarts: tool calls already made are repeated. If it acks before, a crash loses the event. Decide: ack on receipt after persisting the event to the crew's checkpointer, then run; or quorum queues with `x-delivery-limit` and dead-letter to `lost-hail` after N. The doc names `lost-hail` and nothing about its policy or who reads it.
- **Action idempotency.** `event_id` dedupe prevents double-processing an event; it does not prevent `dispatch_team` being called twice by a restarted run. Give every action tool an optional `idempotency_key` (crews pass `event_id:step`) and have the Ship systems dedupe. Conformance should test it.
- **Station concurrency.** One station handles several incidents (one LangGraph thread per `incident_id`); fine but unstated. Worse: KEDA scales Ops to N replicas on one queue, so two Ops pods can process two events of the same incident at once. Use RabbitMQ single-active-consumer per station queue, or a consistent-hash exchange on `incident_id` so an incident sticks to one replica, or state in the doc that stations are singletons and KEDA scales only across incidents. Pick one.
- **Comms loops.** In choreography, stations consume comms as inputs. A `report` that triggers a `report` that triggers an `ack` is a loop with no termination other than the token budget. Define: which `kind`s a station may react to (requests and orders addressed to it; never acks; never reports unless it requested), and a per-incident message cap enforced by the Ship (drop and log past N messages per station per incident).
- **Envelope is missing correlation fields.** No `message_id`, `in_reply_to`/`correlation_id`, `ship_time`, `seq`. `ack` cannot name what it acknowledges; Science cannot hand a brief back to the requesting station without `in_reply_to`. The `text` cap has no number; `payload` has no per-kind schema.
- **Routing keys for comms.** `comms.#` only. Define `comms.<channel>.<kind>` (or `comms.<incident_id>.<to>`) so a station can bind to orders addressed to it or to `all-hands` without consuming the whole channel. Also `crew.heartbeat` and `incident.closed` keys are named; `order` arrival key is not.
- **Spoofing.** With one RabbitMQ user, a crew can publish `alert.*` (fake an event), `incident.closed` (close its own incident), or a heartbeat for a station it does not run. RabbitMQ topic permissions (per-user write/read regexes on the `subspace` exchange) are the enforcement and they are not mentioned. Compose: put the crew on a `crew-net` that has only the bus, the MCP services and the gateway attached; the default network makes `postgres:5432` reachable with default credentials.
- **Heartbeat liveness.** No TTL; a dead station stays "thinking" on the panel forever. Define interval and stale threshold; the Stations panel shows `standby` (or a Mycroft `QUEUED`/`STANDBY` condition) after 3 missed beats.

### D. Human-in-the-loop: approval enforcement, stuck interrupts, the harness captain

- **Enforce at the Ship.** Make the consequential action tools (`seal_section`, `detain`, `quarantine`, `isolate_subsystem`, and decide on `restrict_lifts`, `reroute_power`) require an `order_id` that the Captain's chair issued for that incident and action, or return a structured refusal "requires captain authorization". Then "escalations warranted" is Ship-observable, a crew cannot skip approval, and conformance can test it. This moves the interrupt from a Crew-side nicety to a contract rule, which is what the doc's own boundary philosophy says it should be. The screen's Ops line "Lifts on deck 7 restricted" taken without approval while sealing needs approval shows the policy is currently arbitrary.
- **Scripted captain.** The Final Problem runs unattended. Every episode that escalates correctly (the no-good-outcome episode by design) will block on an interrupt. Define a `captain_policy` per episode or per run (auto-approve, auto-deny, approve-after-N-seconds, approve only listed actions) that the harness plays, and a timeout that resolves the interrupt as `escalated` outcome. Without this the harness hangs.
- **Resume transport.** The open decision is honest, and it is bigger than captain orders: Science handing a brief back to Medical is the same primitive (a station waits for a comms reply). In LangGraph: checkpointer with `thread_id = incident_id`, `interrupt()` on wait, a consumer that receives the order/reply and invokes `Command(resume=...)`. Blocking wait with timeout is simpler and works for a demo, but then the station's consumer is blocked, prefetch matters, and KEDA scale-to-zero can kill a waiting pod (with a Postgres checkpointer the next pod can resume; with blocking wait the wait is lost). Decide at step 5, as the doc says, but note the dependency on C.

### E. Outcome judging

- **When.** On `file_report` receipt, at the next tick, or continuously? If a report lands one tick before `infected_cured` flips, is it a false claim? Define: judge evaluates at the tick boundary after the report; `fail` conditions evaluated every tick regardless of reports.
- **Failed report path.** Crew claims resolved, Ship says no. Does the incident stay open with a `report_rejected` comms message? Does the crew get a reason? Is it scored as a wrong action? Undefined, and it is exactly the "crew lies" case the doc highlights.
- **Multiple reports.** Two stations file for the same incident; or a report with no `incident_id`. Define: one report per incident per station; the Ship takes the first.
- **Unreachable win conditions.** `win: {infected_cured: true}`: `infected_cured` and `casualties` are not in `state:` and no reaction sets them. The sketch cannot be executed as written; the format needs derived variables and a reaction that cures.
- **Partial outcomes.** `partial: casualties <= 3` and `fail: casualties > 3` overlap with `win: casualties: 0`; precedence order (win, then partial, then fail) must be stated.

### F. Archive and write-back

- **Poisoning.** The crew writes its own summary into the ship's log at close. A crew that applied the wrong remedy and got `partial` can write "sedative resolved the outbreak". The next run retrieves it with HIGH confidence. The doc knows this (pattern-break rationale) but leaves the record body to the crew. Have the Ship stamp outcome, scorecard, and the actual action list onto the record server-side and make `file_record` accept only the crew's narrative fields; rank by outcome in `similar_incidents` so failed remedies surface as warnings, not precedents.
- **Timing.** `file_record` is a Librarian action tool the crew can call any time, including before close, for any `incident_id`. Restrict it to the incident's own id after `incident.closed`, or make write-back Ship-initiated from the final report.
- **Embedding model change.** Dimension change forces a column migration and full re-index; say so next to "re-run on every change to chunking or the embedding model".
- **Retrieval eval data.** Where do the needle/phrasing pairs come from? `archive_seed` already names the needle per episode; add `probes: [phrasings]` to it and the retrieval eval set writes itself.
- **Hybrid search detail.** Chunk-level RRF needs collapsing to record ids before top-k; `similar_incidents(symptoms[])` presumably restricts to the two incident collections. Fine, just state it.

### G. Gateway (Warp Core)

- **429 is the wrong code.** LangChain's OpenAI client (and LiteLLM) retry 429 with backoff by default; a budget refusal will be retried two or three times, burning time, then raise a generic rate-limit error the crew may handle as transient. Since the doc cannot mandate client config ("no code interface"), use a status the clients do not retry (402 or 403) with a structured body, and put it in the contract. Conformance tests that the crew escalates on it.
- **Budget units and reset.** "Dilithium budget per incident" in tokens, dollars, or both? Reset per run? Does Impulse mode (free) count tokens against it? The screen shows per-incident and per-hour gauges; the doc defines per-incident only.
- **Headers.** `X-Incident-Id` and `X-Station` per request: with `ChatOpenAI` this is `default_headers` at client construction or `extra_headers` per call; the incident changes per run, so the reference crew needs a client per incident or per-call headers. Doable; say which.
- **Response cache key.** "(model, prompt, temperature)" must be the full request body (messages, tools, tool_choice, temperature, model). Tool schemas change the answer.
- **Ollama via OpenAI-compatible endpoint.** Ollama's `/v1/chat/completions` tool-calling support has lagged its native `/api/chat` (streaming tool calls, `tool_choice`); route LiteLLM to Ollama with the `ollama_chat/` provider rather than `openai/` against port 11434 to avoid silent degradations. Structured output: Ollama supports a JSON schema `format`; make sure the gateway passes `response_format` through.
- **Ollama concurrency.** `OLLAMA_NUM_PARALLEL` divides the KV cache across slots; on a 16 to 24 GB laptop a 7 to 8B model at 8K context × 4 slots is tight and will fall back to CPU or evict. Embedding model and chat model loaded together need `OLLAMA_MAX_LOADED_MODELS >= 2` or they thrash. Say what hardware the maker has; the doc's open decision gestures at it.
- **Build timing.** With LiteLLM, the gateway is a day's work. It should exist at step 2 so every scorecard from step 3 onward has tokens and cost from one source and every model call has a span. Deferring it to step 10 means re-plumbing six stations later.
- **LiteLLM alternatives.** LiteLLM has per-key budgets and spend tracking; a virtual key per run could replace part of the thin FastAPI layer. Worth a sentence in build vs buy.

### H. LangGraph specifics

- "one span per node" is not free: LangGraph does not emit OTel spans; use an OpenInference/OpenLLMetry LangChain instrumentor or a custom callback handler, and extract the `traceparent` from the AMQP header into the run's context manually. Name the choice.
- `recursion_limit` is the "max tool iterations" mechanism; the escalation on hitting it must be caught (`GraphRecursionError`) and turned into an `escalation` message, not a crash.
- Checkpointer: `langgraph-checkpoint-postgres` in the crew's own Postgres (crew-private, which contradicts "no database credentials" as noted).
- Small-model tool calling through LangChain's `bind_tools` on Ollama models: works for Qwen-family; expect malformed arguments and a retry/validation node per station. The "strict schemas on every tool" mitigation needs a validator node in the graph; say so.

### I. MCP specifics

- Streamable HTTP sessions are stateful by default (`Mcp-Session-Id`). If a system runs more than one replica, or restarts mid-incident, sessions break. Run FastMCP in stateless mode or pin one replica per system. For "mocked but stateful" with state in Postgres, stateless HTTP is the right default.
- Each station connects to 2 or 3 MCP servers; `langchain-mcp-adapters` handles multi-server tool loading. Fine. Tool count per station of 4 to 6 is right for small models.
- Who may call what: nothing stops Medical calling `seal_section`. Either every station gets every server (and the eval scores misuse), or the Ship issues per-station tokens with tool allowlists. The station table implies allowlists; the contract does not.
- MCP calls are not on the bus, so the Holodeck cannot see them; see B (internal action topic).

### J. Observability

- A trace per incident with a root span open for minutes and spans arriving from five processes is fine in Jaeger, but someone must own the root span context: persist `traceparent` in the incident table and have the Ship set it on every event it relays for that incident. Spans from events that arrive before the incident exists (the first event) need a different parent; decide that the first event's span is the root.
- Alternative worth stating: one trace per station run, linked to an incident span via span links. Jaeger's UI handles links poorly; SigNoz better. This is actually the deciding factor between the two backends and the doc does not mention it.
- Prometheus metrics named (queue depth, incidents open, tokens per minute, cost per hour) need an exporter each: RabbitMQ's built-in Prometheus plugin, the Ship API, the gateway. Fine.

### K. Kubernetes

- **NetworkPolicy is not enforced** by kind's default kindnet or by Docker Desktop's Kubernetes. The doc's "that is the 'enforce it physically' rule done the production way" is false on the named target unless the cluster is created with `disableDefaultCNI: true` and Calico or Cilium installed. Either do that and say so, or drop the claim.
- `host.docker.internal:11434` from a pod: the kind node container resolves it, but pods go through CoreDNS, which forwards to the node's upstream resolver; whether that resolves `host.docker.internal` depends on the Docker Desktop version. The reliable pattern is a selector-less Service plus an Endpoints/EndpointSlice pointing at the host gateway IP, or `hostAliases` on the gateway pod. Only the gateway needs it, which is a point in favor of the gateway design.
- CloudNativePG stock images lack pgvector; use an image with the extension or build one. A detail, but it will cost an evening.
- KEDA RabbitMQ scaler with a waiting (blocking) consumer: the message is unacked, `messages_ready` is 0, KEDA may scale the station to zero mid-wait depending on the mode (`QueueLength` via management API counts total messages; AMQP mode counts ready). Needs `minReplicaCount: 1` for any station that holds interrupts, which removes the "zero pods" headline.
- Operators (RabbitMQ cluster operator, CloudNativePG) plus KEDA plus Jaeger/SigNoz plus OTel DaemonSet on a laptop kind cluster is a lot of memory beside Ollama on the host. The doc should state a target machine.

### L. Things that read as generic output

The Kubernetes bullets and the Observability backend paragraph. "Prompt caching on system prompts and tool schemas" without noting that it only applies to the Anthropic path and needs `cache_control` markers passed through LiteLLM. "Tilt or Skaffold if an inner loop on the cluster turns out to be wanted." The model-name list.

### M. Things that will not work as described

- NetworkPolicy on kind/Docker Desktop defaults (K).
- Budget refusal as 429 (G).
- "Same pair always produces the same world" without a simulated clock (A).
- Doyle sketch as written (win condition on undefined variables; `advance` only on act 1; no tick definition) (E, and section 7).
- `reactions.on: {tool: ...}` without an action stream (B).
- Scale-to-zero stations holding interrupts (K, D).
- "Crew container receives exactly a bus URL" with a LangGraph Postgres checkpointer (section 2 item 3).

---

## 5. Artifact-by-artifact notes

### (a) Architecture doc, section by section

- **Pitch.** Good. States the real point (separation, comparison with evidence). The "writes its own episodes" tagline oversells: the Holodeck runs authored Doyle files with seeded parameters; it does not write episodes. A panel may ask whether an LLM authors scenarios; the answer is no, and the tagline should not imply yes.
- **Goals and non-goals.** Clear and measurable. "Provably" should be "measurably". The non-goal "docker compose up" is at odds with the k8s section's ambition.
- **Three layers.** The table is the right artifact. Two cells are wrong (Ship never touches which crew is running; Crew never touches Ship databases while bringing its own). The separation rule is good; "Enforced physically" overclaims.
- **Component diagram.** Not in the export; cannot judge. The README promises it as the headline.
- **The Ship contract.** The best section. Events: rename `stardate`; add `episode_id`/`run_id`, `ship_time`, source system; keep `act` out. Systems: the tool table is the right granularity but has no signatures. Comms: see envelope gaps. Outcomes: `file_report` needs a home; judging needs timing rules.
- **Holodeck and episodes.** The ideas (acts with triggers, reactions, red herrings, interleaving, three layers of randomness, pattern-break) are strong. The Doyle sketch is not executable and the clock is undefined. "Determinism" overclaims.
- **Crew.** Strong. The station table should carry an approval-required column and a tool allowlist. The "Rules every crew follows" need the loop and idempotency rules from section 4C. "Two implementations make a contract real" is the line to keep.
- **The Archive and the Librarian.** Good design, good demo. Add write-back trust (4F) and the probes-in-archive_seed idea.
- **Comms channel.** Good principles; incomplete envelope; the example's style conflicts with Mycroft's voice rule. "Click-through to the trace" and "the captain talks on it" are the two things that make this more than a chat log; keep.
- **LLM strategy.** The Warp Core subsection is the most production-minded part of the document and belongs earlier in the build. Model names are placeholders; pricing claims need verification; the 429 choice is wrong.
- **Observability.** Right intent, day-one is right. Root span ownership and the per-node span mechanism are missing.
- **Evals.** Excellent. Metric definitions and the Doyle blocks they depend on are missing. Add a model-latency column and a wall-time budget.
- **Bridge UI.** Panel table is fine. The Incidents panel's "act" column breaks the design rule two paragraphs later.
- **Tech stack and repo layout.** Fine. Add `ship/clock` or wherever the logical clock lives, and `ship/desk` for the incident/report system.
- **Running it locally.** Compose reasoning is right; k8s section needs the corrections in 4K or needs to be cut to "later".
- **Build order.** Mostly right; see section 6 for the reorder.
- **Open decisions.** Honest and the right items, missing the biggest one (clock) and the second biggest (Holodeck-Ship interface).
- **Glossary.** Useful; contains the IP slips and the name collisions.

### (b) The bridge screen

**Does it let a human follow the incident?** Partly. A viewer can see who is at station, what each is doing, that Science found a precedent and Medical is verifying it, that the XO wants deck 7 sealed and the captain must decide, and that a coolant incident closed earlier. That is a good story for one screenful. Where it fails:

- **No incident id on comm lines.** Two incidents are open and the Comms frame shows lines from both interleaved; nothing on a CommLine says which incident it belongs to. The doc's example puts `INC-0042` on every line. The rail has per-incident channels (`inc42` selected) but the lines shown are from both incidents, so either the rail selection is not filtering or the fixture ignores it. Either way, the thing the doc says makes the Interleaving episode interesting (keeping two incidents separate) is not followable on the screen.
- **Lines out of time order.** Medical 00:04:03 after Security 00:04:06; Science 00:04:04 after that. If the channel is grouped by incident, say so visually; if it is one stream, sort it.
- **Tool calls inline.** The doc's restraint rule says tool calls live in a muted toggleable layer. The screen shows them inline with no toggle. Information-design-wise the inline tool line (`MANIFEST.list_section_occupants(deck=7, section=12)` with result "3 crew listed · 4 lifeforms scanned") is actually the most informative line on the screen; so either revise the doc rule to "tool lines are shown muted inline, toggle to hide", or implement the toggle.
- **XO in a choreography crew.** The subtitle says choreography; the roster has an incident-owning XO. For a hiring audience who reads the doc first, this reads as "the maker does not know which crew is running".
- **Incident state words** do not match the doc (Resolved is not a state; INC-0042 should be awaiting_captain).
- **Act column** reveals Holodeck structure.
- **Fixture time errors** (INC-0041 resolved in the future; INC-0042 elapsed wrong). Trivial to fix; corrosive if a reviewer notices.
- **Dilithium header 59 %** is unexplained; per-incident gauges are good but should say "used".
- **Who requested Science?** Medical says "not in sickbay records" and Science then searches; no `request` line links them. The doc's comms model is request/reply; the screen shows parallel monologues.
- **Pending escalation card** is the best element: title, origin, time, rationale, two buttons, a confirm dialog that states the consequences. It would be better if it showed which station will execute the order and which MCP action it authorizes (the thing the Ship would enforce under 4D).

**Does it match the doc's panels and contract?** Comms, Incidents, Stations, Captain's chair are present (the four the doc says make up the live demo screen). Dilithium and a Timeline are also present; the doc lists Dilithium as a drill-down. Tricorder click-through is not shown (no trace id on lines). Replay is absent (fine for a live screen).

**Shown but not provided by the contract:** per-station tool-call counts and "last message" times on AgentCards (not in the heartbeat; would need the Ship's action log or OTel); station `role` captions; per-incident and per-hour Dilithium percentages (the doc defines per-incident budget only); "Tokens this hour", "Est. cost", "Tool calls" readouts (Ship audit table, fine, but sourced from a gateway that does not exist until step 10); alert condition and its detail text (no source defined); Act number (Holodeck internals); "Judged against hidden state: win, no casualties" (from `incident.closed`, fine).

**Provided by the contract but not shown:** `trace_id` click-through; `severity` on events; the `kind` enum (hail/request/report/ack/order/escalation) as a visible shape; `incident_id` per line; the comms `internal` layer toggle; station `detail` captions (errored/rate-limited); which pending action requires approval and who holds the interrupt; `awaiting_captain` state on the incident.

### (c) Design system vs doc vocabulary

- CommLine `kind` (Mycroft: message/tool/finding/decision/system) vs envelope `kind` (doc: hail/request/report/ack/order/escalation). Needs an explicit mapping table (e.g. request→message, report→finding, escalation→decision with accent, order→decision from captain, ack→muted message, tool→internal layer, event→system).
- Condition words (Mycroft, fixed: NOMINAL/DEGRADED/CRITICAL/STANDBY/QUEUED) vs incident states (doc) vs screen words. Decide what a Status pill on an incident row says: probably the doc's state in uppercase, not Mycroft's ship conditions, and update Mycroft to allow it.
- Agent state words (idle/thinking/acting/standby) are consistent between doc and Mycroft; Cascade behavior for `standby` is unspecified in Mycroft.
- Division assignment is consistent (command/ops/science; security and engineering in ops; medical and library in science) except Mycroft's "sensors analysis" under science vs Ops owning Sensors in the doc.
- Ship's computer: Crew in Mycroft, Ship in the doc.
- Voice: first-person sentences (Mycroft) vs clipped protocol lines with no narration (doc). The doc's output protocol wins on cost grounds; Mycroft's voice section should be revised to "clipped protocol lines, first person allowed, no narration of intent" and the `text` cap should be the design constraint that keeps lines short.
- Time format HH:MM:SS: consistent. Mycroft's "No dates on the console" matches the doc's "never a stardate".
- Mycroft's "RED ALERT" vs doc's budget "Red Alert": conflict noted.
- Mycroft forbids the franchise's font name and stardates; the doc's `stardate` field name and "Starfleet-style" violate the shared rule.
- Tokens: status-* lack yellow-alert values; the screen's default condition is yellow.

---

## 6. Plan credibility

**Effort estimate** (one person, part-time, call it 100 to 120 hours over eight or nine weeks):

- Step 1 Spine: 6 to 8 h. Plus the logical clock if added here: +4 h.
- Step 2 One system, one station: 20 to 30 h. The sink is small-model tool calling: schema validation retries, prompt iteration, Ollama memory tuning. Everyone underestimates this.
- Step 3 Judgment and harness: 10 to 15 h, more if the Holodeck-Ship interface (system state in Postgres, action stream) is built here, which it must be for the judge to work: +8 h.
- Step 4 Second crew, contract, conformance: 10 to 12 h.
- Step 5 Comms and captain: 15 to 20 h. Interrupt/resume plumbing plus the scripted captain plus Security station.
- Step 6 Bridge UI: 25 to 35 h even with the design system (WebSocket feed, state, four panels, replay).

That is 90 to 130 hours for the "minimum demonstrable project". Steps 7 to 11:

- Step 7 Archive: 20 to 30 h; the hidden cost is authoring four collections of plausible content (regulations, manuals, fleet records) and the retrieval eval set.
- Step 8 Doyle parser and five episodes: 15 to 20 h; the expression language is a rabbit hole.
- Step 9 Remaining stations and crew-xo: 15 to 20 h.
- Step 10 Warp mode: 8 to 12 h with LiteLLM.
- Step 11 Polish, README, charts, GIF: 10 to 15 h.

Total 160 to 230 hours. The plan is a four-to-five-month plan at part-time, not two.

**Which step is most underestimated:** step 2 (local model tool calling) in time, step 7 (content authoring) in effort nobody budgets, and step 5 (async resume primitive, which also serves Science request/reply) in design difficulty. The Kubernetes section has no step at all and could consume two weekends on its own.

**Most likely way it stalls:** the maker spends weeks tuning an Ops station on a 7B model to reliably locate an intruder, the harness shows crew-rules winning everything, and the project has an environment and no story. Second most likely: the UI absorbs the remaining time because it is the visible part, and the scorecard (the evidence the audience needs) never gets produced.

**Most likely way it fails to demonstrate what it claims:** the evals run on a wall clock, the local crew loses to the remote crew for latency reasons, and a panel member points out the confound. Or the before/after retrieval chart is one run each, not twenty seeds with variance.

**Reorder suggestions:**

1. Put the logical clock in step 1. It is cheap now and expensive later.
2. Put the gateway (LiteLLM plus a 100-line budget/header/span layer) in step 2. Every station after that gets cost and spans for free.
3. Build the internal action stream and system state in Postgres in step 2 (the systems need them anyway); the judge in step 3 reads them.
4. Add the scripted captain in step 5, same day as the interrupt.
5. Consider swapping steps 6 and 7: the scorecard and the before/after chart are what the README audience evaluates; the screen can be a later weekend because the design system already exists. If the demo GIF matters more to the maker, keep the order but cap step 6 at the four panels.
6. Delete the Kubernetes work from the two-month plan entirely. Keep the section in the doc as "deployment story, planned", with the corrections from 4K. A compose-only project with a real scorecard beats a kind cluster with a demo.

**What to cut first, in order:** Kubernetes/KEDA/operators; crew-xo and the runtime-comparison track (step 4 in coordination models); Medical and Engineering stations (keep Ops, Security, Science: intruder plus research is enough story); SigNoz profile; Replay scrubber; Holodeck console UI (a CLI is fine); the Doyle expression language (Python callables registered by name, as the open decision already suggests); text-to-speech. Keep at all costs: Ship-judged outcomes, crew-rules baseline, 20-seed held-out scorecard, the archive before/after, the Warp Core, the comms channel with the captain in it.

---

## 7. Distance from a spec

The doc is a narrative with one YAML sketch and two field tables. A spec.md that a person or a coding agent could build from without questions needs the following, listed as the missing artifacts.

### Schemas (JSON Schema or pydantic, in `ship/contract/`)

1. `Event` (full): `event_id`, `run_id`, `episode_id`, `incident_id` (or the decision that events carry none), `routing_key`, `severity`, `source_system`, `observed` (per routing key: `alert.security.intruder`, `alert.medical.symptoms`, `alert.engineering.coolant`, each with its own `observed` schema), `ship_time`, `traceparent`.
2. `CommsEnvelope`: add `message_id`, `in_reply_to`, `ship_time`, `seq`, `text` max length (a number), per-`kind` `payload` schemas (request: `task`, `to`; report: `findings`, `sources[]`, `confidence`; escalation: `requested_action`, `tool`, `args`, `rationale`; order: `order_id`, `authorizes: [{tool, args}]`, `in_reply_to`; ack: `in_reply_to`).
3. `Heartbeat`: `crew`, `stations[]` with `name`, `index`, `division`, `state`, `activity`, `detail`, `ts`; interval and stale threshold.
4. `Report` (the `file_report` payload): `incident_id`, `station`, `claim` (resolved|escalated|cannot_resolve), `summary` (capped), `actions_taken[]`, `sources[]`, `confidence`.
5. `IncidentClosed` / scorecard: `incident_id`, `run_id`, `outcome`, `ship_time_open`, `ship_time_closed`, `casualties`, `correct_actions[]`, `wrong_actions[]`, `red_herring_calls`, `escalations[]` with `warranted` bool, `sources_used[]`, `turns`, `tool_calls`, `tokens_in/out/cached`, `cost_usd`, `model_latency_total`.
6. `ActionEvent` (internal): `system`, `tool`, `args`, `station`, `incident_id`, `event_id`, `idempotency_key`, `order_id`, `ship_time`, `result_summary`.
7. MCP tool signatures for all seven systems (~25 tools): argument schema, return schema (the "five fields"), error schema (including `requires_authorization`), idempotency behavior, which stations may call it.
8. Manifest data model: decks, sections, persons (name, role, crew|passenger, assigned section, flags), lifeforms; the Holodeck-writable truth tables vs the observable views.
9. Archive record schema (fleet incident and ship's log): sections (`symptoms`, `cause`, `remedy`, `outcome`), metadata, chunking rules, embedding model and dimension, index type (HNSW params), RRF constant, top-k.
10. Budget: units (tokens and USD), scope (per incident, per run, per hour), enforcement response (status code and body), what counts in Impulse mode.
11. WebSocket message types for the UI (comms line, event, heartbeat, incident update, budget update, alert condition).
12. Replay record format (what is persisted per line, and the scrub granularity).

### Algorithms and semantics

13. Clock: definition of a tick, mapping to wall time, behavior during `awaiting_captain`, speed control for evals, how `elapsed` and `ship_time` are stamped.
14. Incident assignment: how an event becomes part of an incident (Holodeck-tagged, Ship-correlated by rules, or crew-opened), and how crews express "these two are linked" so the Interleaving episode is scorable.
15. Incident state machine: states, allowed transitions, who may transition (Ship only, or crew via `claim_step`), what "step" means and who authors steps per incident.
16. Outcome judge: when it runs, precedence among win/partial/fail/escalated, what happens on a rejected report, max reports per incident, timeout behavior.
17. Approval policy: list of tools requiring an order, how an order authorizes an action (`order_id` on the tool call), timeout and default, the scripted captain policy format for evals.
18. Event-to-incident routing of orders and replies: routing-key grammar for `comms.*`, which bindings a station must declare, which `kind`s it may react to.
19. Redelivery and acks: queue type (quorum), prefetch, ack timing, `x-delivery-limit`, DLQ policy for `lost-hail`, whether DLQ'd events count against the crew.
20. Concurrency: one consumer per station or N replicas; per-incident stickiness; LangGraph thread keying.
21. Loop prevention: per-incident, per-station message caps; which kinds may trigger responses.
22. Context construction per station turn: which messages are included, ordering, truncation policy, history retention across events of one incident.
23. Sensor noise application: where (Holodeck or system), per-tool parameters from the episode's `sensors:` block, seeding.
24. Determinism contract: what the gateway response cache keys on; what must be excluded from prompts for reruns to hit it.
25. Scorecard metric definitions: formula for each row in the Evals table, including "warranted" escalation and "chased a red herring".
26. Seed split: how tuning vs held-out seeds are chosen and recorded, and how the README states which set a chart came from.
27. Write-back: who writes what into the ship's log record (crew narrative vs Ship-stamped outcome), when, and how `similar_incidents` ranks failed outcomes.
28. Trace model: root span ownership for an incident, parenting of events and station runs, span attributes list, the instrumentation library for LangGraph.
29. Heartbeat liveness and the Stations panel's stale behavior.
30. Alert condition rule for the bridge (what sets yellow/red).

### Grammar

31. Doyle: full schema for `title`, `synopsis`, `difficulty`, `tags`, `seed_default`, `params` (distributions: `choice`, `uniform`, `sample`, `from`), `state` (with derived variables such as `infected_cured`, `casualties`), `sensors`, `acts` (`id`, `when`, `emit`, `advance`, `red_herring`, `once|repeat`, `every`), `reactions` (`on` matcher over the ActionEvent, `effect`), `resolution` (precedence, `escalated` as a win), `expected_actions`, `escalation_policy` (which actions should be escalated in this episode), `decoys` (which tool calls count as chasing the red herring), `captain_policy`, `archive_seed` with `probes`, `interleave` (link to another episode, causal flag). Expression language: the tiny evaluator's grammar (operators, functions such as `occupants(deck)`, `elapsed`), or the registered-callable convention.
32. Comms `text` style grammar: `FROM → TO · INC · text`, max length, allowed punctuation, the enum vocabulary for actions.

### Acceptance criteria

33. Per build step: what "runnable" means (step 1: a Jaeger trace with these spans; step 2: Ops files a report that passes schema validation on N of 10 runs; step 3: scorecard table with these columns for 10 seeds; step 4: both crews pass conformance tests T1..Tn; step 5: an order resumes an interrupted run within one tick; step 6: the four panels render the live feed and a replay).
34. Conformance suite test list: redelivery idempotency, invalid envelope rejected, order honored, budget refusal escalates, unauthorized action refused, heartbeat cadence, report schema.
35. Retrieval eval set format and thresholds (recall@5 >= x on the seed probes).
36. Target hardware and model: the machine, the Ollama model and quantization, context length, `OLLAMA_NUM_PARALLEL`, and the acceptance tool-call success rate on a fixed prompt set.
37. Repo conventions: Python version, uv, ruff config, test layout, compose profile names, environment variables for every service, port map.
38. Wall-time and cost budget for a full season run in each drive mode.

With those, the document is a spec. Realistically the first eleven schemas and items 13 to 17 are what step 1 to 3 need; the rest can be filled in step by step, which is consistent with "slowly become a spec" as long as each build step adds its own section.

---

## 8. Top ten findings, ranked

1. **The clock is undefined and it confounds the headline comparison.** Ship time vs wall time is never specified; with wall-clock ticks the local-vs-remote scorecard measures latency and the "same seed, same world" claim is false. *Action:* add a Ship-owned logical clock (lockstep or ratio-with-pause) to step 1, stamp `ship_time` on every event and envelope, add a model-latency column to the scorecard, and rewrite the Determinism paragraph to state its conditions.

2. **The Holodeck-to-Ship interface does not exist in the document.** How truth reaches sensors, how action calls reach `reactions`, where system state lives, who seeds the Manifest. *Action:* specify a Ship Postgres `world` schema (Holodeck-writable) with observable views the systems read, and an internal `action.<system>.<tool>` topic every action tool publishes on; the Holodeck and the scorecard consume it. Build in step 2.

3. **Captain approval is crew-side policy, so the boundary has a hole where human-in-the-loop lives, and unattended evals will hang on interrupts.** *Action:* consequential tools require an `order_id` issued by the Captain's chair (Ship-enforced, conformance-tested); add a `captain_policy` to Doyle and a harness captain with timeouts; make `escalated` a first-class outcome.

4. **Incident assignment contradicts the interleaving test.** Events carry `incident_id`, yet the crew is supposed to decide whether two events are one incident. *Action:* pick one model. Recommended: Holodeck tags events with a `thread` the Ship maps to incidents; crews may `link_incidents` through the Incident Desk and the scorecard rewards or penalizes the link against hidden truth.

5. **Boundary enforcement will not hold on the named platforms.** kind/Docker Desktop do not enforce NetworkPolicy; one RabbitMQ user can spoof events and close incidents; compose default network exposes Postgres; crews need their own DB. *Action:* RabbitMQ per-crew user with topic permissions on `subspace` (write `comms.*|crew.*`, read `alert.*|comms.*|incident.*`); a `crew-net` compose network with only bus, MCP and gateway; rewrite "exactly a bus URL" to "no Ship credentials"; either install Calico/Cilium on kind or remove the NetworkPolicy claim.

6. **The gateway is deferred to step 10 but is the only place cost, budget and model spans come from; and 429 is retried by every client.** *Action:* stand up LiteLLM plus a thin budget/header/span layer at step 2; refuse over-budget calls with 402 or 403 and a structured body; define budget units and scope; key the response cache on the full request body.

7. **Redelivery, idempotency, concurrency and loops are named, not designed.** `event_id` dedupe does not cover repeated actions; N replicas of one station can act on one incident; stations reacting to reports will loop. *Action:* idempotency keys on action tools; quorum queues with delivery limits and a stated DLQ policy; single-active-consumer or incident-sticky routing per station; per-incident message caps and a list of which `kind`s a station may react to; add `message_id` and `in_reply_to` to the envelope.

8. **The scorecard depends on Doyle blocks that do not exist, and the archive trusts the crew's self-report.** *Action:* add `expected_actions`, `escalation_policy`, `decoys`, derived state variables and resolution precedence to Doyle; have the Ship stamp outcome and the actual action list onto ship's-log records server-side and rank failed outcomes as warnings in `similar_incidents`; add `probes` to `archive_seed` to generate the retrieval eval set.

9. **Vocabulary has fragmented across doc, screen and Mycroft, and the doc breaks its own IP rule.** Three enums for comm kinds, three for incident state, Red Alert and Ship's Log each meaning two or three things, Sensors as system and station, Tactical/Security vs Security, the `stardate` field, "Starfleet-style", "Jefferies tube". *Action:* one canonical vocabulary table in `ship/contract` (wire enums) with an explicit wire-to-Mycroft display mapping; rename `stardate` to `ship_time`; remove the two franchise terms; rename the budget event; split Ship's Log from Incident Records.

10. **The bridge screen does not let a viewer follow two interleaved incidents.** No incident id per line, lines out of order, tool calls inline against the doc's rule, an XO on a choreography bridge, an Act column leaking Holodeck structure, fixture times in the future, an unexplained Dilithium header. *Action:* add an incident chip to CommLine (or make the rail filter real), sort by time, mute tool lines with a toggle, relabel the screen as crew-xo or remove the XO, drop Act, fix the fixture timestamps, label gauges "used", and show which action the pending order authorizes.

### Three strongest aspects to preserve

1. **Ship-judged outcomes against hidden truth, with held-out seeds, variance, and pattern-break episodes as their own column.** This is the spine of the demonstration and it is better than most production eval practice. Lead with it in the README; defend it with the clock fix.

2. **The network boundary as the interface, proven by a second (no-LLM) crew and a conformance suite, with the rules crew as the baseline every agent crew must beat.** "Two implementations make a contract real; one makes a guess" is the sentence a panel remembers. Keep crew-rules first in the build order no matter what else is cut.

3. **The Warp Core as architecture, not config, together with the output protocol and its reasons.** One Ship-owned endpoint for routing, fairness, budget, cache and spans; tool calls as the only output; short tool results because models mirror what they are fed. These are the details that tell a reviewer the author has paid for tokens and debugged verbose agents. Move the gateway earlier and fix the status code, and this section does most of the credibility work.
