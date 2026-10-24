import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { Status } from "./Status";
import type { Level } from "./shared";

describe("Status", () => {
    it.each([
        ["ok", "Nominal"],
        ["warn", "Degraded"],
        ["crit", "Critical"],
        ["info", "Standby"],
    ] as const)("%s shows the word %s", (level: Level, word: string) => {
        render(<Status level={level} />);
        const status: HTMLElement = screen.getByRole("status");
        expect(status).toHaveTextContent(word);
        expect(status).toHaveClass("my-status", `my-status-${level}`);
    });

    it("defaults to info", () => {
        render(<Status />);
        expect(screen.getByRole("status")).toHaveClass("my-status-info");
    });

    it("children replace the default word", () => {
        render(<Status level="info">Awaiting captain</Status>);
        expect(screen.getByRole("status")).toHaveTextContent("Awaiting captain");
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(<Status level="crit" />);
    });
});
