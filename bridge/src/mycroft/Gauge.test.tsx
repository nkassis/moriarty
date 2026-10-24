import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { Gauge } from "./Gauge";

function cells(meter: HTMLElement): Element[] {
    return [...(meter.querySelector(".my-gauge-bar")?.children ?? [])];
}

describe("Gauge", () => {
    it("is a meter named by its label with the value shown", () => {
        render(<Gauge label="INC-0042 used" level={0.31} value="31 %" />);
        const meter: HTMLElement = screen.getByRole("meter", { name: "INC-0042 used" });
        expect(meter).toHaveAttribute("aria-valuenow", "0.31");
        expect(meter).toHaveClass("my-gauge", "my-tone-primary");
        expect(meter.querySelector(".my-gauge-value")).toHaveTextContent("31 %");
    });

    it("lights cells from the bottom, 20 by default", () => {
        render(<Gauge label="g" level={0.31} />);
        const all: Element[] = cells(screen.getByRole("meter"));
        expect(all).toHaveLength(20);
        expect(all.filter((c) => c.classList.contains("on"))).toHaveLength(6);
        expect(all[all.length - 1]).toHaveClass("on");
        expect(all[0]).not.toHaveClass("on");
    });

    it.each([
        [1, 4],
        [10, 10],
        [100, 60],
    ])("clamps %s segments to %s", (segments: number, expected: number) => {
        render(<Gauge label="g" level={0.5} segments={segments} />);
        expect(cells(screen.getByRole("meter"))).toHaveLength(expected);
    });

    it("marks warn and crit zones and switches state at the thresholds", () => {
        const { rerender } = render(
            <Gauge label="g" level={0.58} segments={10} warn={0.7} crit={0.9} />,
        );
        const meter: HTMLElement = screen.getByRole("meter");
        const top: Element[] = cells(meter);
        expect(top[0]).toHaveClass("z-crit");
        expect(top[1]).toHaveClass("z-warn");
        expect(top[2]).toHaveClass("z-warn");
        expect(top[3]).not.toHaveClass("z-warn");
        expect(meter).not.toHaveClass("my-gauge-warn");
        rerender(<Gauge label="g" level={0.7} segments={10} warn={0.7} crit={0.9} />);
        expect(screen.getByRole("meter")).toHaveClass("my-gauge-warn");
        rerender(<Gauge label="g" level={0.95} segments={10} warn={0.7} crit={0.9} />);
        expect(screen.getByRole("meter")).toHaveClass("my-gauge-crit");
    });

    it("sets the bar height through a custom property", () => {
        render(<Gauge label="g" level={0.5} height={110} />);
        expect(screen.getByRole("meter").style.getPropertyValue("--my-gauge-height")).toBe("110px");
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(<Gauge label="g" level={0.8} warn={0.7} crit={0.9} value="80 %" />);
    });
});
