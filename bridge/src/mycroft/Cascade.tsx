import { useEffect, useState, type CSSProperties, type ReactElement, type ReactNode } from "react";
import type { AgentState } from "../contract/enums";
import { cx, toneClass, useReducedMotion, type Tone } from "./shared";
import "./Cascade.css";

export const STATE_WORD: Readonly<Record<AgentState, string>> = {
    idle: "Idle",
    thinking: "Thinking",
    acting: "Acting",
    standby: "Standby",
};

export interface CascadeProps {
    state?: AgentState;
    rows?: number;
    cols?: number;
    /** Colour of the hot cells; ops by default. */
    tone?: Tone;
    className?: string;
}

function seed(r: number, c: number, t: number): string {
    return String((r * 7919 + c * 104729 + t * 31) % 10000).padStart(4, "0");
}

/** A small grid of ticking numerals: still when idle or on standby, or when motion is reduced. */
export function Cascade({
    state = "idle",
    rows = 2,
    cols = 3,
    tone,
    className,
}: CascadeProps): ReactElement {
    const reduced: boolean = useReducedMotion();
    const [tick, setTick] = useState<number>(0);
    const live: boolean = (state === "thinking" || state === "acting") && !reduced;
    useEffect(() => {
        if (!live) return;
        const id: ReturnType<typeof setInterval> = setInterval(
            () => {
                setTick((t) => t + 1);
            },
            state === "acting" ? 120 : 320,
        );
        return () => {
            clearInterval(id);
        };
    }, [live, state]);

    const cells: ReactNode[] = [];
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            const hot: boolean = live && (r * cols + c + tick) % 5 === 0;
            cells.push(
                <span
                    key={`${String(r)}-${String(c)}`}
                    className={cx("my-cascade-cell", hot && "hot")}
                >
                    {seed(r, c, live ? tick : 0)}
                </span>,
            );
        }
    }
    const style: CSSProperties = { "--my-cascade-cols": cols } as CSSProperties;
    return (
        <div
            className={cx("my-cascade", `my-cascade-${state}`, toneClass(tone, "ops"), className)}
            style={style}
            role="img"
            aria-label={STATE_WORD[state]}
        >
            {cells}
        </div>
    );
}
