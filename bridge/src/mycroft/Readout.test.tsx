import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { Readout } from "./Readout";

describe("Readout", () => {
    it("shows label, value and unit, primary by default", () => {
        const { container } = render(<Readout label="Cost, run" value="0.07" unit="USD" />);
        const root: Element | null = container.firstElementChild;
        expect(root).toHaveClass("my-readout", "my-tone-primary");
        expect(root?.querySelector(".my-readout-label")).toHaveTextContent("Cost, run");
        expect(root?.querySelector(".my-readout-value")).toHaveTextContent("0.07USD");
        expect(root?.querySelector(".my-readout-unit")).toHaveTextContent("USD");
        expect(root?.querySelector(".my-readout-leader")).toHaveAttribute("aria-hidden", "true");
    });

    it("has no meter without a level", () => {
        render(<Readout label="Ship time" value="00:04:12" />);
        expect(screen.queryByRole("meter")).toBeNull();
    });

    it("draws a ten-cell meter named by the label", () => {
        render(<Readout label="Budget used" value="41" unit="%" level={0.41} tone="quiet" />);
        const meter: HTMLElement = screen.getByRole("meter", { name: "Budget used" });
        expect(meter).toHaveAttribute("aria-valuenow", "0.41");
        expect(meter.children).toHaveLength(10);
        expect(meter.querySelectorAll(".on")).toHaveLength(4);
    });

    it.each([
        [-0.5, 0],
        [0.04, 0],
        [0.05, 1],
        [1, 10],
        [3, 10],
    ])("level %s lights %s cells", (level: number, lit: number) => {
        render(<Readout label="L" value="v" level={level} />);
        expect(screen.getByRole("meter").querySelectorAll(".on")).toHaveLength(lit);
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(<Readout label="Budget used" value="41" unit="%" level={0.41} />);
    });
});
