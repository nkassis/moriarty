import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { AlertBanner } from "./AlertBanner";

describe("AlertBanner", () => {
    afterEach(() => {
        document.documentElement.removeAttribute("data-theme");
    });

    it("yellow shows Condition yellow on the warn fill", () => {
        render(<AlertBanner condition="yellow" detail="Unlisted lifeform on deck 7" />);
        const alert: HTMLElement = screen.getByRole("alert");
        expect(alert).toHaveClass("my-alert", "my-alert-yellow");
        expect(alert).toHaveTextContent("Condition yellow");
        expect(alert.querySelector(".my-alert-detail")).toHaveTextContent("deck 7");
    });

    it("red shows Red alert; children replace the word", () => {
        const { rerender } = render(<AlertBanner condition="red" />);
        expect(screen.getByRole("alert")).toHaveClass("my-alert-red");
        expect(screen.getByRole("alert")).toHaveTextContent("Red alert");
        rerender(<AlertBanner condition="red">Intruder alert</AlertBanner>);
        expect(screen.getByRole("alert")).toHaveTextContent("Intruder alert");
    });

    it("offers Stand down only with a handler", async () => {
        const onStandDown = vi.fn();
        const { rerender } = render(<AlertBanner condition="yellow" />);
        expect(screen.queryByRole("button")).toBeNull();
        rerender(<AlertBanner condition="yellow" onStandDown={onStandDown} />);
        await userEvent.click(screen.getByRole("button", { name: "Stand down" }));
        expect(onStandDown).toHaveBeenCalledOnce();
    });

    it("leaves the page theme alone by default", () => {
        render(<AlertBanner condition="red" />);
        expect(document.documentElement).not.toHaveAttribute("data-theme");
    });

    it("with setTheme, switches <html> data-theme and restores it on unmount", () => {
        document.documentElement.setAttribute("data-theme", "standard");
        const { rerender, unmount } = render(<AlertBanner condition="yellow" setTheme />);
        expect(document.documentElement).toHaveAttribute("data-theme", "yellow-alert");
        rerender(<AlertBanner condition="red" setTheme />);
        expect(document.documentElement).toHaveAttribute("data-theme", "red-alert");
        unmount();
        expect(document.documentElement).toHaveAttribute("data-theme", "standard");
    });

    it("with setTheme, removes the attribute on unmount when there was none", () => {
        const { unmount } = render(<AlertBanner condition="red" setTheme />);
        unmount();
        expect(document.documentElement).not.toHaveAttribute("data-theme");
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(<AlertBanner condition="yellow" detail="detail" />);
    });
});
