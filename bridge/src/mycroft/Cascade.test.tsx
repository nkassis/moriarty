import { act, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { Cascade } from "./Cascade";

function numerals(): string[] {
    return [...screen.getByRole("img").children].map((c) => c.textContent);
}

function mockReducedMotion(reduced: boolean): void {
    vi.spyOn(window, "matchMedia").mockImplementation(
        (query: string) =>
            ({
                matches: reduced,
                media: query,
                onchange: null,
                addEventListener: () => undefined,
                removeEventListener: () => undefined,
                addListener: () => undefined,
                removeListener: () => undefined,
                dispatchEvent: () => false,
            }) satisfies MediaQueryList,
    );
}

describe("Cascade", () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });
    afterEach(() => {
        vi.useRealTimers();
        vi.restoreAllMocks();
    });

    it("is an image named by the state word, idle by default", () => {
        render(<Cascade />);
        const img: HTMLElement = screen.getByRole("img", { name: "Idle" });
        expect(img).toHaveClass("my-cascade", "my-cascade-idle", "my-tone-ops");
        expect(img.children).toHaveLength(6);
    });

    it("sizes the grid from rows and cols", () => {
        render(<Cascade rows={3} cols={4} state="standby" tone="science" />);
        const img: HTMLElement = screen.getByRole("img", { name: "Standby" });
        expect(img.children).toHaveLength(12);
        expect(img.style.getPropertyValue("--my-cascade-cols")).toBe("4");
        expect(img).toHaveClass("my-tone-science");
    });

    it("stays still when idle", () => {
        render(<Cascade state="idle" />);
        const before: string[] = numerals();
        act(() => {
            vi.advanceTimersByTime(2000);
        });
        expect(numerals()).toEqual(before);
        expect(screen.getByRole("img").querySelector(".hot")).toBeNull();
    });

    it("ticks while thinking and acting", () => {
        render(<Cascade state="thinking" />);
        const before: string[] = numerals();
        act(() => {
            vi.advanceTimersByTime(320);
        });
        expect(numerals()).not.toEqual(before);
        expect(screen.getByRole("img").querySelector(".hot")).not.toBeNull();
    });

    it("stays still when the user prefers reduced motion", () => {
        mockReducedMotion(true);
        render(<Cascade state="acting" />);
        const before: string[] = numerals();
        act(() => {
            vi.advanceTimersByTime(1000);
        });
        expect(numerals()).toEqual(before);
    });

    it("stops its timer on unmount", () => {
        const { unmount } = render(<Cascade state="acting" />);
        unmount();
        expect(vi.getTimerCount()).toBe(0);
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(<Cascade state="standby" />);
    });
});
