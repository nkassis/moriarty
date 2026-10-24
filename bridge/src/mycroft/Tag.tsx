import type { ReactElement, ReactNode } from "react";
import { cx, toneClass, type Tone } from "./shared";
import "./Tag.css";

// Not in bundle.js: Tag is the small sender pill the bundle draws inside Timeline (.my-tl-from),
// lifted out so a label chip can stand on its own. Same recipe, no new visual.

export interface TagProps {
    /** Pill colour; primary by default. A division tone marks crew. */
    tone?: Tone;
    children: ReactNode;
    className?: string;
}

export function Tag({ tone, children, className }: TagProps): ReactElement {
    return <span className={cx("my-tag", toneClass(tone, "primary"), className)}>{children}</span>;
}
