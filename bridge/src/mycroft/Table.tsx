import type { CSSProperties, KeyboardEvent, ReactElement, ReactNode } from "react";
import { cx, toneClass, type Tone } from "./shared";
import "./Table.css";

export type RowKey = string | number;

export interface TableColumn<Row> {
    key: string;
    header: ReactNode;
    /** num: right-aligned tabular mono. */
    kind?: "num";
    /** Column width; a number is px. */
    width?: number | string;
    /** Renders the cell; without it the row's string or number field `key` is shown. */
    cell?: (row: Row, index: number) => ReactNode;
}

export interface TableProps<Row extends object> {
    columns: readonly TableColumn<Row>[];
    rows: readonly Row[];
    /** Defaults to the row's position. */
    rowKey?: (row: Row, index: number) => RowKey;
    /** Header band colour; primary by default. */
    tone?: Tone;
    caption?: ReactNode;
    selected?: RowKey;
    /** Makes rows selectable by click, Enter or Space. */
    onSelect?: (key: RowKey, row: Row) => void;
    className?: string;
}

function fieldOf(row: object, key: string): ReactNode {
    const value: unknown = (row as Record<string, unknown>)[key];
    return typeof value === "string" || typeof value === "number" ? value : null;
}

function widthStyle(width: number | string | undefined): CSSProperties | undefined {
    if (width === undefined) return undefined;
    const value: string = typeof width === "number" ? `${String(width)}px` : width;
    return { "--my-col-width": value } as CSSProperties;
}

export function Table<Row extends object>({
    columns,
    rows,
    rowKey,
    tone,
    caption,
    selected,
    onSelect,
    className,
}: TableProps<Row>): ReactElement {
    return (
        <table className={cx("my-table", toneClass(tone, "primary"), className)}>
            {caption != null ? <caption className="my-table-caption">{caption}</caption> : null}
            <thead>
                <tr>
                    {columns.map((c) => (
                        <th
                            key={c.key}
                            scope="col"
                            className={cx("my-table-th", c.kind === "num" && "num")}
                            style={widthStyle(c.width)}
                        >
                            {c.header}
                        </th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {rows.map((r, i) => {
                    const k: RowKey = rowKey ? rowKey(r, i) : i;
                    const isSelected: boolean = selected === k;
                    const select = onSelect
                        ? (): void => {
                              onSelect(k, r);
                          }
                        : undefined;
                    const onKeyDown = select
                        ? (e: KeyboardEvent<HTMLTableRowElement>): void => {
                              if (e.key === "Enter" || e.key === " ") {
                                  e.preventDefault();
                                  select();
                              }
                          }
                        : undefined;
                    return (
                        <tr
                            key={k}
                            className={cx(isSelected && "selected", select && "clickable")}
                            aria-selected={select ? isSelected : undefined}
                            tabIndex={select ? 0 : undefined}
                            onClick={select}
                            onKeyDown={onKeyDown}
                        >
                            {columns.map((c) => (
                                <td
                                    key={c.key}
                                    className={cx("my-table-td", c.kind === "num" && "num")}
                                >
                                    {c.cell ? c.cell(r, i) : fieldOf(r, c.key)}
                                </td>
                            ))}
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
}
