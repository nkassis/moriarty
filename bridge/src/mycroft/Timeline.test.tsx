import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { Timeline, type TimelineEvent } from "./Timeline";

const EVENTS: readonly TimelineEvent[] = [
    {
        id: "a1",
        time: "00:03:58",
        from: "Sensors",
        level: "warn",
        title: "Lifeform count mismatch",
        children: "Deck 7 section 12, one more than the manifest lists.",
    },
    { id: "a2", time: "00:04:04", from: "Ops", tone: "ops", title: "Lifeform located" },
    { id: "a3", time: "00:04:11", title: "Order requested" },
];

describe("Timeline", () => {
    it("is an ordered list with one item per event", () => {
        render(<Timeline events={EVENTS} />);
        expect(within(screen.getByRole("list")).getAllByRole("listitem")).toHaveLength(3);
    });

    it("shows time, sender chip, title and body", () => {
        render(<Timeline events={EVENTS} />);
        const first: HTMLElement = screen.getAllByRole("listitem")[0] as HTMLElement;
        expect(first.querySelector(".my-tl-time")).toHaveTextContent("00:03:58");
        expect(within(first).getByText("Sensors")).toHaveClass("my-tag", "my-tl-from");
        expect(first.querySelector(".my-tl-title")).toHaveTextContent("Lifeform count mismatch");
        expect(first.querySelector(".my-tl-text")).toHaveTextContent("Deck 7 section 12");
        expect(first.querySelector(".my-tl-mark")).toHaveAttribute("aria-hidden", "true");
    });

    it("colours the mark by level, else by tone", () => {
        render(<Timeline events={EVENTS} />);
        const [warn, ops, plain] = screen.getAllByRole("listitem");
        expect(warn).toHaveClass("my-tl-warn");
        expect(warn).not.toHaveClass("my-tone-primary");
        expect(ops).toHaveClass("my-tone-ops");
        expect(within(ops as HTMLElement).getByText("Ops")).toHaveClass("my-tone-ops");
        expect(plain).toHaveClass("my-tone-primary");
        expect(plain?.querySelector(".my-tl-from")).toBeNull();
        expect(plain?.querySelector(".my-tl-text")).toBeNull();
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(<Timeline events={EVENTS} />);
    });
});
