import type { ReactElement, ReactNode } from "react";
import { cx, type Level } from "./shared";
import "./Status.css";

const WORDS: Readonly<Record<Level, string>> = {
    ok: "Nominal",
    warn: "Degraded",
    crit: "Critical",
    info: "Standby",
};

export interface StatusProps {
    /** Fill colour and default word; info (Standby) by default. */
    level?: Level;
    /** Replaces the default word. Always a word: the colour never carries meaning alone. */
    children?: ReactNode;
    className?: string;
}

export function Status({ level = "info", children, className }: StatusProps): ReactElement {
    return (
        <span className={cx("my-status", `my-status-${level}`, className)} role="status">
            {children ?? WORDS[level]}
        </span>
    );
}
