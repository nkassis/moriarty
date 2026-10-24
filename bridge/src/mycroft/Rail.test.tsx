import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { Rail, type RailItem } from "./Rail";

const NAV: readonly RailItem[] = [
    { id: "season", label: "Scenarios" },
    { id: "bridge", label: "Bridge" },
    { id: "director", label: "Director" },
    { id: "scorecard", label: "Scorecard" },
    { id: "log", label: "Log", index: "05" },
];

describe("Rail", () => {
    it("is a named navigation landmark of buttons", () => {
        render(<Rail items={NAV} label="Screens" />);
        const nav: HTMLElement = screen.getByRole("navigation", { name: "Screens" });
        expect(within(nav).getAllByRole("button")).toHaveLength(5);
    });

    it("defaults the landmark name to Rail", () => {
        render(<Rail items={NAV} />);
        expect(screen.getByRole("navigation", { name: "Rail" })).toBeInTheDocument();
    });

    it("cycles default tones and fills the last segment", () => {
        render(<Rail items={NAV} />);
        const segs: HTMLElement[] = screen.getAllByRole("button");
        expect(segs.map((s) => [...s.classList].find((c) => c.startsWith("my-tone-")))).toEqual([
            "my-tone-primary",
            "my-tone-secondary",
            "my-tone-tertiary",
            "my-tone-quiet",
            "my-tone-primary",
        ]);
        expect(segs[4]).toHaveClass("my-rail-seg-fill");
        expect(segs[0]).not.toHaveClass("my-rail-seg-fill");
    });

    it("honours explicit tone and size", () => {
        render(
            <Rail items={[{ label: "Alpha", tone: "accent", size: "tall" }, { label: "Beta" }]} />,
        );
        expect(screen.getByRole("button", { name: "Alpha" })).toHaveClass(
            "my-tone-accent",
            "my-rail-seg-tall",
        );
    });

    it("marks the selected item and reports selection by id", async () => {
        const onSelect = vi.fn();
        render(<Rail items={NAV} selected="bridge" onSelect={onSelect} />);
        const bridge: HTMLElement = screen.getByRole("button", { name: "Bridge" });
        expect(bridge).toHaveAttribute("aria-current", "true");
        expect(bridge).toHaveClass("my-rail-seg-selected");
        expect(screen.getByRole("button", { name: "Director" })).not.toHaveAttribute(
            "aria-current",
        );
        await userEvent.click(screen.getByRole("button", { name: "Director" }));
        expect(onSelect).toHaveBeenCalledWith("director", NAV[2]);
    });

    it("uses the position as id when an item has none", async () => {
        const onSelect = vi.fn();
        render(
            <Rail items={[{ label: "One" }, { label: "Two" }]} selected={1} onSelect={onSelect} />,
        );
        expect(screen.getByRole("button", { name: "Two" })).toHaveAttribute("aria-current", "true");
        await userEvent.click(screen.getByRole("button", { name: "One" }));
        expect(onSelect).toHaveBeenCalledWith(0, { label: "One" });
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(<Rail items={NAV} selected="bridge" />);
    });
});
