import type { ReactElement, ReactNode } from "react";
import type { Division } from "../contract/enums";
import { cx, toneClass, type Tone } from "./shared";
import "./CommLine.css";

/**
 * Display kinds. Wire kinds map onto these in docs/vocabulary.md § Wire to display mapping;
 * tool lines come from the action stream and are the muted internal layer a channel can hide.
 */
export type CommLineKind = "message" | "finding" | "decision" | "system" | "tool";

const KIND_WORD: Readonly<Record<CommLineKind, string>> = {
    message: "",
    tool: "Tool",
    finding: "Finding",
    decision: "Decision",
    system: "System",
};

const DIVISION_TONES: readonly Tone[] = ["command", "ops", "science"];

export interface CommLineProps {
    from: ReactNode;
    index?: ReactNode;
    /** Ship time, HH:MM:SS. */
    time: ReactNode;
    /** Crew sender: the chip wears the division colour and the wide row the crew ground. */
    division?: Division;
    /** Ship sender colour (tertiary by default); ignored when division is set. */
    tone?: Tone;
    kind?: CommLineKind;
    /** Tool lines: the call, e.g. "SENSORS.locate(deck=7)". */
    call?: ReactNode;
    /** Tool lines: the result summary. */
    result?: ReactNode;
    /** Compact (default) for a mixed panel; false is the wide chip layout of a dedicated channel. */
    compact?: boolean;
    /** Compact only: a pill chip (default), or the sender's name inline with a coloured edge. */
    sender?: "pill" | "edge";
    children?: ReactNode;
    className?: string;
}

export function CommLine({
    from,
    index,
    time,
    division,
    tone,
    kind = "message",
    call,
    result,
    compact = true,
    sender = "pill",
    children,
    className,
}: CommLineProps): ReactElement {
    const isCrew: boolean =
        division !== undefined || (tone !== undefined && DIVISION_TONES.includes(tone));
    const edge: boolean = compact && sender === "edge";
    const indexNode = (lead: string): ReactNode =>
        index != null ? (
            <span className="my-comm-index">
                {lead}
                {index}
            </span>
        ) : null;
    const text: ReactNode = <span className="my-comm-text">{children}</span>;

    return (
        <div
            className={cx(
                "my-comm",
                compact ? "my-comm-compact" : "my-comm-wide",
                `my-comm-${kind}`,
                isCrew && "my-comm-crew",
                edge && "my-comm-edge",
                toneClass(division ?? tone, "tertiary"),
                className,
            )}
        >
            {edge ? null : (
                <span className="my-comm-from" title={typeof from === "string" ? from : undefined}>
                    {from}
                    {indexNode("")}
                </span>
            )}
            <div className="my-comm-body">
                {edge ? (
                    <span className="my-comm-name">
                        {from}
                        {indexNode(" ")}
                    </span>
                ) : null}
                {kind !== "message" ? (
                    <span className="my-comm-kind">{KIND_WORD[kind]}</span>
                ) : null}
                {kind === "tool" ? (
                    <span className="my-comm-toolbox">
                        <code className="my-comm-call">{call}</code>
                        {result != null ? <span className="my-comm-result">{result}</span> : null}
                        {children != null ? text : null}
                    </span>
                ) : (
                    text
                )}
            </div>
            <span className="my-comm-time">{time}</span>
        </div>
    );
}
