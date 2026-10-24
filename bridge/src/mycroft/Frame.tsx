import { isValidElement, type ReactElement, type ReactNode } from "react";
import { Rail, type RailProps } from "./Rail";
import { cx, toneClass, type Tone } from "./shared";
import "./Frame.css";

export interface FrameProps {
    title?: ReactNode;
    index?: ReactNode;
    tone?: Tone;
    /** Quiet (default) is a title bar over a well. false draws the elbow frame: page header only. */
    quiet?: boolean;
    /** Elbow frame only: a Rail element, or the props to build one. */
    rail?: ReactElement | RailProps;
    /** Elbow frame only: close the frame with a bottom elbow and bar. */
    footer?: boolean;
    children?: ReactNode;
    className?: string;
}

export function Frame({
    title,
    index,
    tone,
    quiet = true,
    rail,
    footer = false,
    children,
    className,
}: FrameProps): ReactElement {
    const t: string = toneClass(tone, "primary");
    const label: string | undefined = typeof title === "string" ? title : undefined;
    const indexNode = (cls: string): ReactNode =>
        index != null ? <span className={cls}>{index}</span> : null;

    if (quiet) {
        return (
            <section className={cx("my-frame my-frame-quiet", t, className)} aria-label={label}>
                <div className="my-frame-titlebar">
                    {title != null ? (
                        <h2 className="my-frame-quiet-title">
                            {title}
                            {indexNode("my-frame-quiet-index")}
                        </h2>
                    ) : null}
                </div>
                <div className="my-frame-well">{children}</div>
            </section>
        );
    }

    const railNode: ReactNode =
        rail === undefined ? null : isValidElement(rail) ? rail : <Rail {...rail} />;
    return (
        <section
            className={cx("my-frame my-frame-elbow", footer && "my-frame-footer", className)}
            aria-label={label}
        >
            <div className={cx("my-elbow", t)} />
            <div className="my-frame-head">
                <div className={cx("my-frame-bar", t)} />
                {title != null ? (
                    <h2 className={cx("my-frame-title", t)}>
                        {title}
                        {indexNode("my-frame-title-index")}
                    </h2>
                ) : null}
            </div>
            <div className="my-frame-rail">{railNode}</div>
            <div className="my-frame-well">{children}</div>
            {footer ? <div className={cx("my-elbow my-elbow-bottom", t)} /> : null}
            {footer ? (
                <div className="my-frame-foot">
                    <div className={cx("my-frame-bar", t)} />
                </div>
            ) : null}
        </section>
    );
}
