import {
    useEffect,
    useEffectEvent,
    useId,
    useRef,
    type MouseEvent,
    type ReactElement,
    type ReactNode,
} from "react";
import { cx, toneClass, type Tone } from "./shared";
import "./Dialog.css";

const FOCUSABLE: string = "button, [href], input, [tabindex]:not([tabindex='-1'])";

export interface DialogProps {
    open: boolean;
    title: ReactNode;
    /** warn or crit colours the frame with the status; otherwise tone applies. */
    level?: "warn" | "crit";
    /** Frame colour when no level is set; primary by default. */
    tone?: Tone;
    children?: ReactNode;
    /** Buttons under the text. */
    actions?: ReactNode;
    /** Called on Escape and on a click on the scrim. */
    onClose?: () => void;
    className?: string;
}

export function Dialog({
    open,
    title,
    level,
    tone,
    children,
    actions,
    onClose,
    className,
}: DialogProps): ReactElement | null {
    const ref = useRef<HTMLDivElement>(null);
    const titleId: string = useId();
    const close = useEffectEvent((): void => {
        onClose?.();
    });

    useEffect(() => {
        if (!open) return;
        ref.current?.querySelector<HTMLElement>(FOCUSABLE)?.focus();
        const onKey = (e: KeyboardEvent): void => {
            if (e.key === "Escape") close();
        };
        document.addEventListener("keydown", onKey);
        return () => {
            document.removeEventListener("keydown", onKey);
        };
    }, [open]);

    if (!open) return null;
    const t: string = level ? `my-level-${level}` : toneClass(tone, "primary");
    const onScrimClick = (e: MouseEvent<HTMLDivElement>): void => {
        if (e.target === e.currentTarget) onClose?.();
    };
    return (
        // Escape closes from the keyboard; a click on the scrim is the pointer equivalent.
        // eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions
        <div className="my-dialog-scrim" onClick={onScrimClick}>
            <div
                ref={ref}
                role="dialog"
                aria-modal="true"
                aria-labelledby={titleId}
                className={cx("my-dialog", t, className)}
            >
                <div className="my-dialog-elbow" />
                <div className="my-dialog-bar" />
                <div className="my-dialog-body">
                    <h2 id={titleId} className="my-dialog-title">
                        {title}
                    </h2>
                    <div className="my-dialog-text">{children}</div>
                    {actions != null ? <div className="my-dialog-actions">{actions}</div> : null}
                </div>
                <div className="my-dialog-foot" />
            </div>
        </div>
    );
}
