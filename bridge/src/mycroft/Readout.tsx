import type { ReactElement, ReactNode } from "react";
import { cx, toneClass, type Tone } from "./shared";
import "./Readout.css";

const METER_CELLS: number = 10;

export interface ReadoutProps {
    label: ReactNode;
    value: ReactNode;
    unit?: ReactNode;
    /** 0 to 1: adds a ten-cell meter under the readout. */
    level?: number;
    /** Label and meter colour; primary by default. */
    tone?: Tone;
    className?: string;
}

export function Readout({
    label,
    value,
    unit,
    level,
    tone,
    className,
}: ReadoutProps): ReactElement {
    let meter: ReactNode = null;
    if (typeof level === "number") {
        const on: number = Math.max(0, Math.min(METER_CELLS, Math.round(level * METER_CELLS)));
        meter = (
            <div
                className="my-readout-meter"
                role="meter"
                aria-valuemin={0}
                aria-valuemax={1}
                aria-valuenow={level}
                aria-label={typeof label === "string" ? label : undefined}
            >
                {Array.from({ length: METER_CELLS }, (_, i) => (
                    <span key={i} className={i < on ? "on" : ""} />
                ))}
            </div>
        );
    }
    return (
        <div className={cx("my-readout", toneClass(tone, "primary"), className)}>
            <span className="my-readout-label">{label}</span>
            <span className="my-readout-leader" aria-hidden="true" />
            <span className="my-readout-value">
                {value}
                {unit != null ? <span className="my-readout-unit">{unit}</span> : null}
            </span>
            {meter}
        </div>
    );
}
