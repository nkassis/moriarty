import type { CSSProperties, ReactElement, ReactNode } from "react";
import { cx, toneClass, type Tone } from "./shared";
import "./Gauge.css";

export interface GaugeProps {
    label: ReactNode;
    /** 0 to 1. */
    level: number;
    /** Text under the label, e.g. "31 %". */
    value?: ReactNode;
    /** Number of cells, clamped to 4..60; 20 by default. */
    segments?: number;
    /** Level at or above which the lit cells and label turn status-warn. */
    warn?: number;
    /** Level at or above which the lit cells and label turn status-crit. */
    crit?: number;
    tone?: Tone;
    /** Bar height in px; 160 by default. */
    height?: number;
    className?: string;
}

export function Gauge({
    label,
    level,
    value,
    segments = 20,
    warn,
    crit,
    tone,
    height = 160,
    className,
}: GaugeProps): ReactElement {
    const n: number = Math.max(4, Math.min(60, segments));
    const on: number = Math.max(0, Math.min(n, Math.round(level * n)));
    const state: string =
        crit !== undefined && level >= crit
            ? "crit"
            : warn !== undefined && level >= warn
              ? "warn"
              : "";
    const cells: ReactNode[] = [];
    for (let i = n - 1; i >= 0; i--) {
        const frac: number = (i + 1) / n;
        const zone: string =
            crit !== undefined && frac > crit
                ? "z-crit"
                : warn !== undefined && frac > warn
                  ? "z-warn"
                  : "";
        cells.push(<span key={i} className={cx(i < on && "on", zone)} />);
    }
    const style: CSSProperties = { "--my-gauge-height": `${String(height)}px` } as CSSProperties;
    return (
        <div
            className={cx(
                "my-gauge",
                toneClass(tone, "primary"),
                state && `my-gauge-${state}`,
                className,
            )}
            role="meter"
            aria-valuemin={0}
            aria-valuemax={1}
            aria-valuenow={level}
            aria-label={typeof label === "string" ? label : undefined}
            style={style}
        >
            <div className="my-gauge-bar">{cells}</div>
            <div className="my-gauge-label">{label}</div>
            {value != null ? <div className="my-gauge-value">{value}</div> : null}
        </div>
    );
}
