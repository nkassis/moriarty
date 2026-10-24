import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { expect } from "vitest";
import { THEMES } from "../src/mycroft/tokens";

/**
 * Themes switch through `data-theme` on a wrapper only: a component's markup is identical in every
 * theme and carries no inline colour, font or spacing.
 */
export function expectThemeIndependent(ui: ReactElement): void {
    const { container, rerender } = render(<div data-theme={THEMES[0]?.id}>{ui}</div>);
    const wrapper: Element | null = container.firstElementChild;
    const first: string = wrapper?.innerHTML ?? "";
    for (const theme of THEMES) {
        rerender(<div data-theme={theme.id}>{ui}</div>);
        expect(container.firstElementChild).toHaveAttribute("data-theme", theme.id);
        expect(container.firstElementChild?.innerHTML).toBe(first);
    }
    for (const el of container.querySelectorAll("[style]")) {
        const style: string = el.getAttribute("style") ?? "";
        const declared: string[] = style
            .split(";")
            .map((d) => d.split(":")[0]?.trim() ?? "")
            .filter((p) => p !== "");
        for (const property of declared) expect(property, style).toMatch(/^--my-/);
    }
}
