import { useState, type ReactElement } from "react";
import { Frame, Status, Table, Timeline, type RowKey, type TableColumn } from "../mycroft";
import { INCIDENTS, TIMELINES, type IncidentRow } from "./sample";

const COLUMNS: readonly TableColumn<IncidentRow>[] = [
    { key: "id", header: "Incident", width: 100 },
    { key: "owner", header: "Owner", width: 90 },
    { key: "opened", header: "Opened", kind: "num", width: 90 },
    { key: "elapsed", header: "Elapsed", kind: "num", width: 90 },
    { key: "linked", header: "Linked", width: 80 },
    {
        key: "state",
        header: "State",
        width: 170,
        cell: (r) => <Status level={r.level}>{r.word}</Status>,
    },
];

/** Incidents is a Table plus the selected incident's Timeline. */
export function KitIncidents(): ReactElement {
    const [selected, setSelected] = useState<RowKey>("INC-0042");
    const id: string = String(selected);
    return (
        <div className="kit-stack">
            <Frame title="Incidents" tone="secondary">
                <Table
                    columns={COLUMNS}
                    rows={INCIDENTS}
                    rowKey={(r) => r.id}
                    selected={selected}
                    onSelect={setSelected}
                    tone="secondary"
                />
            </Frame>
            <Frame title={`${id} · Timeline`} tone="tertiary">
                <Timeline events={TIMELINES[id] ?? []} />
            </Frame>
        </div>
    );
}
