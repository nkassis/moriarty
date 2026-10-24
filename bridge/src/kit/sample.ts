// Sample content for the kit, taken from docs/design/Main.dc.html (the live bridge artboard).

import type { Division } from "../contract/enums";
import type {
    AgentCardProps,
    CommLineKind,
    Level,
    RailItem,
    TimelineEvent,
    Tone,
} from "../mycroft";

export interface SampleLine {
    inc: string;
    from: string;
    index?: string;
    time: string;
    division?: Division;
    tone?: Tone;
    kind: CommLineKind;
    call?: string;
    result?: string;
    text?: string;
}

export const COMMS: readonly SampleLine[] = [
    {
        inc: "INC-0043",
        from: "Sickbay",
        time: "00:00:00",
        tone: "tertiary",
        kind: "system",
        text: "Symptom report, deck 7: one case, euphoria and impaired judgment.",
    },
    {
        inc: "INC-0043",
        from: "Medical",
        index: "05",
        time: "00:00:12",
        division: "science",
        kind: "message",
        text: "I opened INC-0043 for the deck 7 case and am pulling the sickbay history for that section.",
    },
    {
        inc: "INC-0043",
        from: "Medical",
        index: "05",
        time: "00:02:30",
        division: "science",
        kind: "finding",
        text: "Six cases now, same two symptoms. Nothing in sickbay records matches, so I am asking Science for a precedent.",
    },
    {
        inc: "INC-0042",
        from: "Sensors",
        time: "00:03:58",
        tone: "tertiary",
        kind: "system",
        text: "Lifeform count, deck 7 section 12: four scanned, three listed.",
    },
    {
        inc: "INC-0042",
        from: "Ops",
        index: "02",
        time: "00:04:01",
        division: "ops",
        kind: "message",
        text: "I opened INC-0042 for the count mismatch. Treating it as separate from the medical case until something links them.",
    },
    {
        inc: "INC-0042",
        from: "Ops",
        index: "02",
        time: "00:04:02",
        division: "ops",
        kind: "tool",
        call: "MANIFEST.list_section_occupants(deck=7, section=12)",
        result: "3 crew listed · 0.2 s",
    },
    {
        inc: "INC-0042",
        from: "Ops",
        index: "02",
        time: "00:04:03",
        division: "ops",
        kind: "tool",
        call: "SENSORS.locate(deck=7, section=12, unlisted=true)",
        result: "timeout (retryable) · retried with same key · 1 unlisted, moving to 14",
    },
    {
        inc: "INC-0043",
        from: "Science",
        index: "04",
        time: "00:04:04",
        division: "science",
        kind: "tool",
        call: "LIBRARY.similar_incidents(symptoms=[euphoria, impaired_judgment])",
        result: "2 records · 0.3 s",
    },
    {
        inc: "INC-0042",
        from: "Ops",
        index: "02",
        time: "00:04:04",
        division: "ops",
        kind: "finding",
        text: "One unlisted lifeform in section 12, unarmed on scan, moving toward section 14. I am asking Security for a team at the lift.",
    },
    {
        inc: "INC-0043",
        from: "Science",
        index: "04",
        time: "00:04:05",
        division: "science",
        kind: "finding",
        text: "Fleet record FLT-2241 matches on both symptoms: waterborne contagion, remedy on file, outcome win. Brief sent to Medical with the record cited.",
    },
    {
        inc: "INC-0042",
        from: "Security",
        index: "03",
        time: "00:04:06",
        division: "ops",
        kind: "decision",
        text: "Team 2 is on its way to the deck 7 lift, ETA 40 ticks. I am restricting the deck 7 lifts now; that needs no order.",
    },
    {
        inc: "INC-0042",
        from: "Security",
        index: "03",
        time: "00:04:11",
        division: "ops",
        kind: "decision",
        text: "Requesting an order to seal deck 7 sections 10 to 16. Sealing needs the captain; the team holds at the lift until then.",
    },
    {
        inc: "INC-0042",
        from: "Bulkheads",
        time: "00:04:11",
        tone: "tertiary",
        kind: "system",
        text: "seal_section refused: requires authorization. Order requested, ORD-0007 pending.",
    },
];

export const CHANNELS: readonly string[] = ["All", "INC-0042", "INC-0043"];

export interface IncidentRow {
    id: string;
    owner: string;
    opened: string;
    elapsed: string;
    linked: string;
    level: Level;
    word: string;
}

export const INCIDENTS: readonly IncidentRow[] = [
    {
        id: "INC-0042",
        owner: "OPS 02",
        opened: "00:03:58",
        elapsed: "00:00:14",
        linked: "none",
        level: "info",
        word: "Awaiting captain",
    },
    {
        id: "INC-0043",
        owner: "MED 05",
        opened: "00:00:00",
        elapsed: "00:04:12",
        linked: "none",
        level: "warn",
        word: "Investigating",
    },
    {
        id: "INC-0041",
        owner: "ENG 06",
        opened: "00:00:40",
        elapsed: "00:03:00",
        linked: "none",
        level: "ok",
        word: "Closed · win",
    },
];

export const TIMELINES: Readonly<Record<string, readonly TimelineEvent[]>> = {
    "INC-0042": [
        {
            id: "a1",
            time: "00:03:58",
            from: "Sensors",
            level: "warn",
            title: "Lifeform count mismatch",
            children: "Deck 7 section 12, one more than the manifest lists.",
        },
        {
            id: "a2",
            time: "00:04:04",
            from: "Ops",
            tone: "ops",
            title: "Lifeform located",
            children: "Unarmed, moving toward section 14.",
        },
        {
            id: "a3",
            time: "00:04:06",
            from: "Security",
            tone: "ops",
            title: "Team 2 dispatched",
            children: "Lifts restricted. Holding at the lift.",
        },
        {
            id: "a4",
            time: "00:04:11",
            from: "Security",
            tone: "ops",
            level: "info",
            title: "Order requested",
            children: "Seal deck 7 sections 10 to 16. Awaiting captain; clock paused.",
        },
    ],
    "INC-0043": [
        {
            id: "b1",
            time: "00:00:00",
            from: "Sickbay",
            level: "warn",
            title: "Symptoms reported",
            children: "Deck 7, one case.",
        },
        {
            id: "b2",
            time: "00:02:30",
            from: "Medical",
            tone: "science",
            title: "Spread confirmed",
            children: "Six cases. No match in sickbay records.",
        },
        {
            id: "b3",
            time: "00:04:05",
            from: "Science",
            tone: "science",
            title: "Precedent found",
            children: "FLT-2241, remedy on file, outcome win.",
        },
        {
            id: "b4",
            time: "00:04:10",
            from: "Medical",
            tone: "science",
            title: "Verifying remedy",
            children: "Checking the record against current cases before treatment.",
        },
    ],
    "INC-0041": [
        {
            id: "c1",
            time: "00:00:40",
            from: "Engineering",
            level: "warn",
            title: "Coolant pressure drop",
            children: "Deck 4, 9 % over 60 ticks.",
        },
        {
            id: "c2",
            time: "00:03:10",
            from: "Engineering",
            tone: "ops",
            title: "Subsystem isolated",
            children: "Rerouted through conduit 5.",
        },
        {
            id: "c3",
            time: "00:03:40",
            from: "Ship",
            level: "ok",
            title: "Closed: win",
            children: "Judged against hidden state, no casualties, 1 decoy ignored.",
        },
    ],
};

export const CREW: readonly (AgentCardProps & { name: string })[] = [
    {
        name: "Ops",
        division: "ops",
        index: "02",
        role: "Operations · sensors and manifest",
        state: "acting",
        activity:
            "Tracking the unlisted lifeform from section 12 toward 14. Deck 4 sensors are unavailable; I asked Security for eyes.",
        meta: "5 tool calls · 1 retry · 00:04:09",
    },
    {
        name: "Security",
        division: "ops",
        index: "03",
        role: "Operations · teams and bulkheads",
        state: "standby",
        activity: "Team 2 holding at the deck 7 lift. Waiting on the seal order.",
        meta: "2 tool calls · 00:04:11",
    },
    {
        name: "Medical",
        division: "science",
        index: "05",
        role: "Sciences · sickbay",
        state: "thinking",
        activity: "Checking the FLT-2241 remedy against the six cases before I order treatment.",
        meta: "3 tool calls · 00:04:10",
    },
    {
        name: "Science",
        division: "science",
        index: "04",
        role: "Sciences · library and computer",
        state: "idle",
        activity: "Brief filed to Medical: FLT-2241, confidence high.",
        meta: "last message 00:04:05",
    },
    {
        name: "Engineering",
        division: "ops",
        index: "06",
        role: "Operations · power and environment",
        state: "acting",
        activity: "Diagnosing the deck 4 sensor outage. Part requested, repair in 30 ticks.",
        meta: "2 tool calls · 00:04:08",
    },
    // Not on the artboard: a command-division card so the kit shows all three divisions.
    {
        name: "Captain",
        division: "command",
        index: "01",
        role: "Command · the chair",
        state: "standby",
        activity: "Seal order ORD-0007 pending.",
        meta: "1 pending order",
    },
];

export const NAV: readonly RailItem[] = [
    { id: "season", label: "Scenarios" },
    { id: "bridge", label: "Bridge" },
    { id: "director", label: "Director" },
    { id: "scorecard", label: "Scorecard" },
];
