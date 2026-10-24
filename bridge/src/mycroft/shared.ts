import { useEffect, useState } from "react";
import type { Division } from "../contract/enums";
import "./tokens.css";
import "./fonts.css";
import "./base.css";

/** Ship bands plus the three crew divisions; each maps to a `.my-tone-*` class that sets `--tone`. */
export type Tone = "primary" | "secondary" | "tertiary" | "quiet" | "accent" | Division;

/** Status levels, shared by Status, Timeline and Dialog. */
export type Level = "ok" | "warn" | "crit" | "info";

export function toneClass(tone: Tone | undefined, fallback: Tone): string {
    return `my-tone-${tone ?? fallback}`;
}

export function cx(...parts: (string | false | null | undefined)[]): string {
    return parts.filter(Boolean).join(" ");
}

const REDUCED_MOTION: string = "(prefers-reduced-motion: reduce)";

function prefersReducedMotion(): boolean {
    return typeof window !== "undefined" && window.matchMedia(REDUCED_MOTION).matches;
}

export function useReducedMotion(): boolean {
    const [reduced, setReduced] = useState<boolean>(prefersReducedMotion);
    useEffect(() => {
        const mq: MediaQueryList = window.matchMedia(REDUCED_MOTION);
        const onChange = (): void => {
            setReduced(mq.matches);
        };
        mq.addEventListener("change", onChange);
        return () => {
            mq.removeEventListener("change", onChange);
        };
    }, []);
    return reduced;
}
