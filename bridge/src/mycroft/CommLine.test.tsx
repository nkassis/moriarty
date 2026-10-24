import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { CommLine, type CommLineKind } from "./CommLine";

function line(container: HTMLElement): Element {
    const el: Element | null = container.firstElementChild;
    if (el === null) throw new Error("nothing rendered");
    return el;
}

describe("CommLine", () => {
    it("compact message: chip, text, time; ship sender is tertiary", () => {
        const { container } = render(
            <CommLine from="Sensors" time="00:03:58">
                Lifeform count, deck 7 section 12: four scanned, three listed.
            </CommLine>,
        );
        const el: Element = line(container);
        expect(el).toHaveClass("my-comm", "my-comm-compact", "my-comm-message", "my-tone-tertiary");
        expect(el).not.toHaveClass("my-comm-crew");
        expect(screen.getByTitle("Sensors")).toHaveTextContent("Sensors");
        expect(el.querySelector(".my-comm-kind")).toBeNull();
        expect(el.querySelector(".my-comm-text")).toHaveTextContent("four scanned");
        expect(el.querySelector(".my-comm-time")).toHaveTextContent("00:03:58");
    });

    it.each([
        ["finding", "Finding"],
        ["decision", "Decision"],
        ["system", "System"],
        ["tool", "Tool"],
    ] as const)("%s lines carry the kind word %s", (kind: CommLineKind, word: string) => {
        const { container } = render(
            <CommLine from="Ops" time="00:04:04" kind={kind}>
                text
            </CommLine>,
        );
        expect(line(container)).toHaveClass(`my-comm-${kind}`);
        expect(line(container).querySelector(".my-comm-kind")).toHaveTextContent(word);
    });

    it("a division sender is crew and the chip wears the division", () => {
        const { container } = render(
            <CommLine from="Medical" index="05" time="00:02:30" division="science" tone="accent">
                Six cases now.
            </CommLine>,
        );
        expect(line(container)).toHaveClass("my-comm-crew", "my-tone-science");
        expect(screen.getByTitle("Medical")).toHaveTextContent("Medical05");
    });

    it("a division tone also counts as crew", () => {
        const { container } = render(
            <CommLine from="Captain" time="00:04:18" tone="command" kind="decision">
                Make it so.
            </CommLine>,
        );
        expect(line(container)).toHaveClass("my-comm-crew", "my-tone-command");
    });

    it("tool lines show the call and result in the muted layer", () => {
        const { container } = render(
            <CommLine
                from="Ops"
                time="00:04:02"
                division="ops"
                kind="tool"
                call="MANIFEST.list_section_occupants(deck=7, section=12)"
                result="3 crew listed · 0.2 s"
            />,
        );
        const el: Element = line(container);
        expect(el.querySelector("code.my-comm-call")).toHaveTextContent(
            "MANIFEST.list_section_occupants",
        );
        expect(el.querySelector(".my-comm-result")).toHaveTextContent("3 crew listed");
        expect(el.querySelector(".my-comm-text")).toBeNull();
    });

    it("edge sender puts the name inline and drops the chip", () => {
        const { container } = render(
            <CommLine from="Ops" index="02" time="00:04:01" division="ops" sender="edge">
                I opened INC-0042.
            </CommLine>,
        );
        const el: Element = line(container);
        expect(el).toHaveClass("my-comm-edge");
        expect(el.querySelector(".my-comm-from")).toBeNull();
        expect(el.querySelector(".my-comm-name")).toHaveTextContent("Ops 02");
    });

    it("wide layout ignores the edge sender", () => {
        const { container } = render(
            <CommLine from="Ops" time="00:04:01" compact={false} sender="edge">
                text
            </CommLine>,
        );
        const el: Element = line(container);
        expect(el).toHaveClass("my-comm-wide");
        expect(el).not.toHaveClass("my-comm-edge");
        expect(el.querySelector(".my-comm-from")).not.toBeNull();
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(
            <CommLine from="Security" index="03" time="00:04:11" division="ops" kind="decision">
                Requesting an order to seal deck 7.
            </CommLine>,
        );
    });
});
