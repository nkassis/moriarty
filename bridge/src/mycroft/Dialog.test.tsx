import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState, type ReactElement } from "react";
import { describe, expect, it, vi } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { Button } from "./Button";
import { Dialog } from "./Dialog";

function actions(): ReactElement {
    return (
        <>
            <Button tone="quiet">Cancel</Button>
            <Button>Confirm</Button>
        </>
    );
}

describe("Dialog", () => {
    it("renders nothing when closed", () => {
        render(<Dialog open={false} title="Confirm order" />);
        expect(screen.queryByRole("dialog")).toBeNull();
    });

    it("is a modal dialog named by its title, with text and actions", () => {
        render(
            <Dialog open title="Confirm order" level="warn" actions={actions()}>
                Issue order ORD-0007.
            </Dialog>,
        );
        const dialog: HTMLElement = screen.getByRole("dialog", { name: "Confirm order" });
        expect(dialog).toHaveAttribute("aria-modal", "true");
        expect(dialog).toHaveClass("my-dialog", "my-level-warn");
        expect(dialog).toHaveTextContent("Issue order ORD-0007.");
        expect(screen.getByRole("heading", { name: "Confirm order" })).toBeInTheDocument();
    });

    it("uses tone without a level, primary by default", () => {
        const { rerender } = render(<Dialog open title="T" />);
        expect(screen.getByRole("dialog")).toHaveClass("my-tone-primary");
        rerender(<Dialog open title="T" tone="accent" />);
        expect(screen.getByRole("dialog")).toHaveClass("my-tone-accent");
        rerender(<Dialog open title="T" tone="accent" level="crit" />);
        expect(screen.getByRole("dialog")).toHaveClass("my-level-crit");
    });

    it("focuses the first control on open", () => {
        render(<Dialog open title="Confirm order" actions={actions()} />);
        expect(screen.getByRole("button", { name: "Cancel" })).toHaveFocus();
    });

    it("closes on Escape and on a scrim click, not on a click inside", async () => {
        const onClose = vi.fn();
        render(
            <Dialog open title="Confirm order" onClose={onClose}>
                body
            </Dialog>,
        );
        await userEvent.click(screen.getByText("body"));
        expect(onClose).not.toHaveBeenCalled();
        await userEvent.keyboard("{Escape}");
        expect(onClose).toHaveBeenCalledTimes(1);
        const scrim: Element | null = screen.getByRole("dialog").parentElement;
        await userEvent.click(scrim as HTMLElement);
        expect(onClose).toHaveBeenCalledTimes(2);
    });

    it("keeps focus where the user put it when the parent re-renders", async () => {
        // A new onClose each render must not re-run the open effect and pull focus to Preview.
        function Host(): ReactElement {
            const [draft, setDraft] = useState<string>("");
            return (
                <Dialog
                    open
                    title="Order"
                    onClose={() => undefined}
                    actions={<Button>Send</Button>}
                >
                    <Button tone="quiet">Preview</Button>
                    <input
                        aria-label="Order text"
                        value={draft}
                        onChange={(e) => {
                            setDraft(e.target.value);
                        }}
                    />
                </Dialog>
            );
        }
        render(<Host />);
        const input: HTMLElement = screen.getByRole("textbox", { name: "Order text" });
        await userEvent.click(input);
        await userEvent.keyboard("seal");
        expect(input).toHaveFocus();
        expect(input).toHaveValue("seal");
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(
            <Dialog open title="Confirm order" level="warn">
                body
            </Dialog>,
        );
    });
});
