import { useEffect, type ReactElement, type ReactNode } from "react";
import { cx } from "./shared";
import "./AlertBanner.css";

export interface AlertBannerProps {
    condition: "yellow" | "red";
    /** Replaces the default word (Condition yellow, Red alert). */
    children?: ReactNode;
    detail?: ReactNode;
    /**
     * Also switch the page theme: sets data-theme on <html> to yellow-alert or red-alert while
     * mounted and restores it after. Off by default; the yellow-alert tint was judged too strong.
     */
    setTheme?: boolean;
    /** Shows a Stand down button. */
    onStandDown?: () => void;
    className?: string;
}

export function AlertBanner({
    condition,
    children,
    detail,
    setTheme = false,
    onStandDown,
    className,
}: AlertBannerProps): ReactElement {
    useEffect(() => {
        if (!setTheme) return;
        const html: HTMLElement = document.documentElement;
        const prev: string | null = html.getAttribute("data-theme");
        html.setAttribute("data-theme", condition === "red" ? "red-alert" : "yellow-alert");
        return () => {
            if (prev === null) html.removeAttribute("data-theme");
            else html.setAttribute("data-theme", prev);
        };
    }, [condition, setTheme]);

    return (
        <div
            role="alert"
            className={cx(
                "my-alert",
                condition === "red" ? "my-alert-red" : "my-alert-yellow",
                className,
            )}
        >
            <div className="my-alert-cap" />
            <div className="my-alert-word">
                {children ?? (condition === "red" ? "Red alert" : "Condition yellow")}
            </div>
            {detail != null ? <div className="my-alert-detail">{detail}</div> : null}
            {onStandDown ? (
                <button type="button" className="my-alert-stand" onClick={onStandDown}>
                    Stand down
                </button>
            ) : null}
        </div>
    );
}
