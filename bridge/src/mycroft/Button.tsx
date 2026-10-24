import type { ButtonHTMLAttributes, ReactElement, ReactNode } from "react";
import { cx, toneClass, type Tone } from "./shared";
import "./Button.css";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    /** Band colour; primary by default. */
    tone?: Tone;
    /** Pill (default) or block: a block has small radius corners, for grouped controls. */
    shape?: "pill" | "block";
    /** Optional index numeral after the label. */
    index?: ReactNode;
}

export function Button({
    tone,
    shape = "pill",
    index,
    className,
    children,
    type = "button",
    ...rest
}: ButtonProps): ReactElement {
    return (
        <button
            {...rest}
            type={type}
            className={cx(
                "my-btn",
                shape === "block" && "my-btn-block",
                toneClass(tone, "primary"),
                className,
            )}
        >
            <span className="my-btn-label">{children}</span>
            {index != null ? <span className="my-btn-index">{index}</span> : null}
        </button>
    );
}
