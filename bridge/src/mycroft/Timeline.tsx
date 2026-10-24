import type { ReactElement, ReactNode } from "react";
import { cx, toneClass, type Level, type Tone } from "./shared";
import { Tag } from "./Tag";
import "./Timeline.css";

export interface TimelineEvent {
    id?: string | number;
    /** Ship time, HH:MM:SS. */
    time: ReactNode;
    /** Sender chip. */
    from?: ReactNode;
    title: ReactNode;
    /** Status colour for the mark; takes precedence over tone. */
    level?: Level;
    /** Mark and chip colour; primary by default. */
    tone?: Tone;
    children?: ReactNode;
}

export interface TimelineProps {
    events: readonly TimelineEvent[];
    className?: string;
}

export function Timeline({ events, className }: TimelineProps): ReactElement {
    return (
        <ol className={cx("my-timeline", className)}>
            {events.map((e, i) => (
                <li
                    key={e.id ?? i}
                    className={cx(
                        "my-tl-event",
                        e.level ? `my-tl-${e.level}` : toneClass(e.tone, "primary"),
                    )}
                >
                    <span className="my-tl-time">{e.time}</span>
                    <span className="my-tl-mark" aria-hidden="true" />
                    <div className="my-tl-body">
                        <div className="my-tl-head">
                            {e.from != null ? (
                                <Tag tone={e.tone ?? "primary"} className="my-tl-from">
                                    {e.from}
                                </Tag>
                            ) : null}
                            <span className="my-tl-title">{e.title}</span>
                        </div>
                        {e.children != null ? <div className="my-tl-text">{e.children}</div> : null}
                    </div>
                </li>
            ))}
        </ol>
    );
}
