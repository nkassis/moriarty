import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { Table, type TableColumn } from "./Table";

interface Incident {
    id: string;
    owner: string;
    opened: string;
    word: string;
}

const ROWS: readonly Incident[] = [
    { id: "INC-0042", owner: "OPS 02", opened: "00:03:58", word: "Awaiting captain" },
    { id: "INC-0043", owner: "MED 05", opened: "00:00:00", word: "Investigating" },
];

const COLUMNS: readonly TableColumn<Incident>[] = [
    { key: "id", header: "Incident", width: 100 },
    { key: "owner", header: "Owner" },
    { key: "opened", header: "Opened", kind: "num", width: "6rem" },
    { key: "state", header: "State", cell: (r) => <strong>{r.word}</strong> },
];

describe("Table", () => {
    it("renders column headers and cells, with a caption", () => {
        render(<Table columns={COLUMNS} rows={ROWS} caption="Incidents" tone="secondary" />);
        const table: HTMLElement = screen.getByRole("table", { name: "Incidents" });
        expect(table).toHaveClass("my-table", "my-tone-secondary");
        expect(
            within(table)
                .getAllByRole("columnheader")
                .map((h) => h.textContent),
        ).toEqual(["Incident", "Owner", "Opened", "State"]);
        expect(screen.getByRole("cell", { name: "OPS 02" })).toBeInTheDocument();
        expect(screen.getByRole("cell", { name: "Awaiting captain" })).toBeInTheDocument();
    });

    it("right-aligns num columns and sets widths through a custom property", () => {
        render(<Table columns={COLUMNS} rows={ROWS} />);
        const [incident, owner, opened] = screen.getAllByRole("columnheader");
        expect(incident?.style.getPropertyValue("--my-col-width")).toBe("100px");
        expect(owner?.getAttribute("style")).toBeNull();
        expect(opened?.style.getPropertyValue("--my-col-width")).toBe("6rem");
        expect(opened).toHaveClass("num");
        expect(screen.getByRole("cell", { name: "00:03:58" })).toHaveClass("num");
    });

    it("is not interactive without onSelect", () => {
        render(<Table columns={COLUMNS} rows={ROWS} />);
        const row: HTMLElement = screen.getAllByRole("row")[1] as HTMLElement;
        expect(row).not.toHaveAttribute("tabindex");
        expect(row).not.toHaveClass("clickable");
    });

    it("selects rows by click and keyboard, keyed by rowKey", async () => {
        const onSelect = vi.fn();
        render(
            <Table
                columns={COLUMNS}
                rows={ROWS}
                rowKey={(r) => r.id}
                selected="INC-0042"
                onSelect={onSelect}
            />,
        );
        const [, first, second] = screen.getAllByRole("row");
        expect(first).toHaveAttribute("aria-selected", "true");
        expect(first).toHaveClass("selected", "clickable");
        expect(second).toHaveAttribute("aria-selected", "false");
        await userEvent.click(second as HTMLElement);
        expect(onSelect).toHaveBeenLastCalledWith("INC-0043", ROWS[1]);
        (first as HTMLElement).focus();
        await userEvent.keyboard("{Enter}");
        expect(onSelect).toHaveBeenLastCalledWith("INC-0042", ROWS[0]);
        await userEvent.keyboard(" ");
        expect(onSelect).toHaveBeenCalledTimes(3);
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(<Table columns={COLUMNS} rows={ROWS} selected={0} />);
    });
});
