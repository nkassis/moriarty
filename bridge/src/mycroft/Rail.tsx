import type { ReactElement, ReactNode } from "react";
import { cx, toneClass, type Tone } from "./shared";
import "./Rail.css";

export type RailId = string | number;

export interface RailItem {
    /** Defaults to the item's position. */
    id?: RailId;
    label: ReactNode;
    /** Defaults cycle primary, secondary, tertiary, quiet. */
    tone?: Tone;
    /** md is a standard segment; the last item defaults to fill, taking the remaining height. */
    size?: "md" | "tall" | "fill";
    index?: ReactNode;
}

export interface RailProps {
    items: readonly RailItem[];
    selected?: RailId;
    onSelect?: (id: RailId, item: RailItem) => void;
    /** Accessible name of the navigation landmark. */
    label?: string;
    className?: string;
}

const RAIL_DEFAULTS: readonly Tone[] = ["primary", "secondary", "tertiary", "quiet"];

export function Rail({
    items,
    selected,
    onSelect,
    label = "Rail",
    className,
}: RailProps): ReactElement {
    return (
        <nav className={cx("my-rail", className)} aria-label={label}>
            {items.map((item, i) => {
                const id: RailId = item.id ?? i;
                const isSelected: boolean = selected === id;
                const size: RailItem["size"] =
                    item.size ?? (i === items.length - 1 ? "fill" : "md");
                return (
                    <button
                        key={String(id)}
                        type="button"
                        className={cx(
                            "my-rail-seg",
                            size === "tall" && "my-rail-seg-tall",
                            size === "fill" && "my-rail-seg-fill",
                            isSelected && "my-rail-seg-selected",
                            toneClass(
                                item.tone,
                                RAIL_DEFAULTS[i % RAIL_DEFAULTS.length] ?? "primary",
                            ),
                        )}
                        aria-current={isSelected ? "true" : undefined}
                        onClick={
                            onSelect
                                ? () => {
                                      onSelect(id, item);
                                  }
                                : undefined
                        }
                    >
                        <span>{item.label}</span>
                        {item.index != null ? (
                            <span className="my-rail-index">{item.index}</span>
                        ) : null}
                    </button>
                );
            })}
        </nav>
    );
}
