import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { Frame } from "./Frame";
import { Rail } from "./Rail";

describe("Frame", () => {
    it("quiet by default: a named region with a title bar heading and a well", () => {
        render(
            <Frame title="Comms" tone="secondary">
                <p>Channel open</p>
            </Frame>,
        );
        const region: HTMLElement = screen.getByRole("region", { name: "Comms" });
        expect(region).toHaveClass("my-frame-quiet", "my-tone-secondary");
        expect(
            within(region).getByRole("heading", { level: 2, name: "Comms" }),
        ).toBeInTheDocument();
        expect(region.querySelector(".my-frame-well")).toHaveTextContent("Channel open");
        expect(region.querySelector(".my-elbow")).toBeNull();
    });

    it("shows the index beside the title", () => {
        render(<Frame title="Crew" index="06" />);
        expect(screen.getByRole("heading", { name: "Crew06" })).toBeInTheDocument();
    });

    it("has no accessible name when the title is not a string", () => {
        render(<Frame title={<em>Budget</em>} />);
        expect(screen.queryByRole("region")).toBeNull();
        expect(screen.getByRole("heading", { name: "Budget" })).toBeInTheDocument();
    });

    it("elbow frame builds a Rail from props", () => {
        render(
            <Frame
                title="Moriarty"
                quiet={false}
                rail={{ items: [{ id: "bridge", label: "Bridge" }], selected: "bridge" }}
            >
                body
            </Frame>,
        );
        const region: HTMLElement = screen.getByRole("region", { name: "Moriarty" });
        expect(region).toHaveClass("my-frame-elbow");
        expect(region.querySelector(".my-elbow")).toHaveClass("my-tone-primary");
        expect(within(region).getByRole("navigation", { name: "Rail" })).toBeInTheDocument();
        expect(screen.getByRole("button", { name: "Bridge" })).toHaveAttribute(
            "aria-current",
            "true",
        );
        expect(region.querySelector(".my-frame-foot")).toBeNull();
    });

    it("elbow frame accepts a Rail element and a footer", () => {
        render(
            <Frame
                title="Moriarty"
                quiet={false}
                footer
                rail={<Rail label="Screens" items={[{ label: "Bridge" }]} />}
            />,
        );
        expect(screen.getByRole("navigation", { name: "Screens" })).toBeInTheDocument();
        const region: HTMLElement = screen.getByRole("region", { name: "Moriarty" });
        expect(region).toHaveClass("my-frame-footer");
        expect(region.querySelector(".my-elbow-bottom")).not.toBeNull();
        expect(region.querySelector(".my-frame-foot .my-frame-bar")).not.toBeNull();
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(
            <Frame title="Moriarty" quiet={false} rail={{ items: [{ label: "Bridge" }] }}>
                body
            </Frame>,
        );
    });
});
