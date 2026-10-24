import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { Button } from "./Button";

describe("Button", () => {
    it("is a type=button with its label as the accessible name", () => {
        render(<Button>Make it so</Button>);
        const button: HTMLElement = screen.getByRole("button", { name: "Make it so" });
        expect(button).toHaveAttribute("type", "button");
        expect(button).toHaveClass("my-btn", "my-tone-primary");
        expect(button).not.toHaveClass("my-btn-block");
    });

    it("applies tone, block shape and the index numeral", () => {
        render(
            <Button tone="quiet" shape="block" index="04">
                Belay
            </Button>,
        );
        const button: HTMLElement = screen.getByRole("button", { name: "Belay04" });
        expect(button).toHaveClass("my-tone-quiet", "my-btn-block");
        expect(button.querySelector(".my-btn-index")).toHaveTextContent("04");
    });

    it("passes through button props and click handlers", async () => {
        const onClick = vi.fn();
        render(
            <Button type="submit" onClick={onClick}>
                Send
            </Button>,
        );
        const button: HTMLElement = screen.getByRole("button", { name: "Send" });
        expect(button).toHaveAttribute("type", "submit");
        await userEvent.click(button);
        expect(onClick).toHaveBeenCalledOnce();
    });

    it("does not fire when disabled", async () => {
        const onClick = vi.fn();
        render(
            <Button disabled onClick={onClick}>
                Send
            </Button>,
        );
        await userEvent.click(screen.getByRole("button", { name: "Send" }));
        expect(onClick).not.toHaveBeenCalled();
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(<Button tone="accent">Confirm</Button>);
    });
});
