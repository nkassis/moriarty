import { useState, type ReactElement } from "react";
import { Button, CommLine, Frame } from "../mycroft";
import { CHANNELS, COMMS, type SampleLine } from "./sample";

function Line({ line }: { line: SampleLine }): ReactElement {
    const { text, ...props }: SampleLine = line;
    return <CommLine {...props}>{text}</CommLine>;
}

/** The Comms panel: channel tabs and the tool-line toggle, as on the live artboard. */
export function KitComms(): ReactElement {
    const [channel, setChannel] = useState<string>("All");
    const [internal, setInternal] = useState<boolean>(true);
    const lines: SampleLine[] = COMMS.filter(
        (l) => (channel === "All" || l.inc === channel) && (internal || l.kind !== "tool"),
    );
    return (
        <Frame title="Comms">
            <div className="kit-row kit-spread">
                <div className="kit-row">
                    {CHANNELS.map((c) => (
                        <Button
                            key={c}
                            shape="block"
                            tone={channel === c ? "accent" : "quiet"}
                            aria-pressed={channel === c}
                            onClick={() => {
                                setChannel(c);
                            }}
                        >
                            {c}
                        </Button>
                    ))}
                </div>
                <Button
                    shape="block"
                    tone="quiet"
                    onClick={() => {
                        setInternal(!internal);
                    }}
                >
                    {internal ? "Hide tool lines" : "Show tool lines"}
                </Button>
            </div>
            <div className="kit-comms">
                {lines.map((l) => (
                    <Line key={`${l.inc}-${l.time}-${l.from}-${l.kind}`} line={l} />
                ))}
            </div>
        </Frame>
    );
}

/** The other CommLine layouts: wide chips for a dedicated channel, and the edge sender. */
export function KitCommVariants(): ReactElement {
    const finding: SampleLine | undefined = COMMS.find((l) => l.kind === "finding");
    return (
        <Frame title="Channel · wide" tone="tertiary">
            <CommLine from="Sensors" time="00:03:58" compact={false} kind="system">
                Lifeform count, deck 7 section 12: four scanned, three listed.
            </CommLine>
            <CommLine
                from="Ops"
                index="02"
                time="00:04:04"
                division="ops"
                compact={false}
                kind="finding"
            >
                {finding?.text}
            </CommLine>
            <CommLine from="Captain" time="00:04:18" tone="command" compact={false} kind="decision">
                Make it so. Order ORD-0007: seal deck 7 sections 10 to 16. Team 2 holds at the lift.
            </CommLine>
            <div className="kit-gap" />
            <CommLine from="Ops" index="02" time="00:04:01" division="ops" sender="edge">
                I opened INC-0042 for the count mismatch.
            </CommLine>
            <CommLine
                from="Security"
                index="03"
                time="00:04:11"
                division="ops"
                sender="edge"
                kind="decision"
            >
                Requesting an order to seal deck 7 sections 10 to 16.
            </CommLine>
        </Frame>
    );
}
