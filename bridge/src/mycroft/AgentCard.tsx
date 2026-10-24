import type { ReactElement, ReactNode } from "react";
import type { AgentState, Division } from "../contract/enums";
import { Cascade, STATE_WORD } from "./Cascade";
import { cx, toneClass } from "./shared";
import "./AgentCard.css";

export interface AgentCardProps {
    name: ReactNode;
    /** The band wears the division colour; ops by default. */
    division?: Division;
    index?: ReactNode;
    /** Secondary line, e.g. "Operations · sensors and manifest". */
    role?: ReactNode;
    state?: AgentState;
    /** Current activity, one or two sentences. */
    activity?: ReactNode;
    /** Footnote, e.g. "2 tool calls · last 00:04:06". */
    meta?: ReactNode;
    selected?: boolean;
    /** Makes the card a toggle button (aria-pressed follows selected). */
    onClick?: () => void;
    className?: string;
}

export function AgentCard({
    name,
    division = "ops",
    index,
    role,
    state = "idle",
    activity,
    meta,
    selected = false,
    onClick,
    className,
}: AgentCardProps): ReactElement {
    const classes: string = cx(
        "my-agent",
        `my-agent-${state}`,
        toneClass(division, "ops"),
        selected && "my-agent-selected",
        onClick && "clickable",
        className,
    );
    const content: ReactNode = (
        <>
            <div className="my-agent-band">
                <span className="my-agent-name">
                    {name}
                    {index != null ? <span className="my-agent-index">{index}</span> : null}
                </span>
                <span className="my-agent-state">{STATE_WORD[state]}</span>
            </div>
            <div className="my-agent-body">
                <div className="my-agent-top">
                    {role != null ? <span className="my-agent-role">{role}</span> : <span />}
                    <Cascade state={state} rows={2} cols={3} tone={division} />
                </div>
                {activity != null ? <div className="my-agent-activity">{activity}</div> : null}
                {meta != null ? <div className="my-agent-meta">{meta}</div> : null}
            </div>
        </>
    );
    return onClick ? (
        <button type="button" onClick={onClick} className={classes} aria-pressed={selected}>
            {content}
        </button>
    ) : (
        <div className={classes}>{content}</div>
    );
}
