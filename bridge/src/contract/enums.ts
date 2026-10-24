// Contract enums used by the bridge, copied from docs/vocabulary.md § Contract enums.
// Stopgap: replaced by types generated from ship/contract/schema/ in NIM-19. Do not add values here.

export const AGENT_STATES = ["idle", "thinking", "acting", "standby"] as const;
export type AgentState = (typeof AGENT_STATES)[number];

export const DIVISIONS = ["command", "ops", "science"] as const;
export type Division = (typeof DIVISIONS)[number];

export const COMMS_KINDS = ["request", "report", "ack", "order", "escalation", "system"] as const;
export type CommsKind = (typeof COMMS_KINDS)[number];
