import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { AgentCard } from "./AgentCard";

describe("AgentCard", () => {
    it("shows name, index, state word, role, activity and meta", () => {
        const { container } = render(
            <AgentCard
                name="Ops"
                division="ops"
                index="02"
                role="Operations · sensors and manifest"
                state="acting"
                activity="Tracking the unlisted lifeform."
                meta="4 tool calls"
            />,
        );
        const card: Element | null = container.firstElementChild;
        expect(card?.tagName).toBe("DIV");
        expect(card).toHaveClass("my-agent", "my-agent-acting", "my-tone-ops");
        expect(card?.querySelector(".my-agent-name")).toHaveTextContent("Ops02");
        expect(card?.querySelector(".my-agent-state")).toHaveTextContent("Acting");
        expect(card?.querySelector(".my-agent-role")).toHaveTextContent("Operations");
        expect(card?.querySelector(".my-agent-activity")).toHaveTextContent("Tracking");
        expect(card?.querySelector(".my-agent-meta")).toHaveTextContent("4 tool calls");
        expect(screen.getByRole("img", { name: "Acting" })).toHaveClass("my-tone-ops");
    });

    it("defaults to ops and idle, and omits empty lines", () => {
        const { container } = render(<AgentCard name="Science" />);
        const card: Element | null = container.firstElementChild;
        expect(card).toHaveClass("my-tone-ops", "my-agent-idle");
        expect(card?.querySelector(".my-agent-activity")).toBeNull();
        expect(card?.querySelector(".my-agent-meta")).toBeNull();
    });

    it.each(["command", "ops", "science"] as const)("wears the %s division", (division) => {
        render(<AgentCard name="X" division={division} state="thinking" />);
        expect(screen.getByRole("img", { name: "Thinking" })).toHaveClass(`my-tone-${division}`);
    });

    it("becomes a toggle button when clickable", async () => {
        const onClick = vi.fn();
        const { rerender } = render(
            <AgentCard name="Medical" division="science" onClick={onClick} />,
        );
        const button: HTMLElement = screen.getByRole("button", { name: /Medical/ });
        expect(button).toHaveAttribute("aria-pressed", "false");
        expect(within(button).getByRole("img", { name: "Idle" })).toBeInTheDocument();
        await userEvent.click(button);
        expect(onClick).toHaveBeenCalledOnce();
        rerender(<AgentCard name="Medical" division="science" onClick={onClick} selected />);
        expect(screen.getByRole("button", { name: /Medical/ })).toHaveAttribute(
            "aria-pressed",
            "true",
        );
        expect(screen.getByRole("button", { name: /Medical/ })).toHaveClass("my-agent-selected");
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(<AgentCard name="Security" index="03" state="standby" />);
    });
});
