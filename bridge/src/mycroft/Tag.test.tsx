import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { expectThemeIndependent } from "../../test/themes";
import { Tag } from "./Tag";

describe("Tag", () => {
    it("renders its text as a primary pill by default", () => {
        render(<Tag>Sensors</Tag>);
        expect(screen.getByText("Sensors")).toHaveClass("my-tag", "my-tone-primary");
    });

    it("takes a ship or division tone", () => {
        render(
            <>
                <Tag tone="tertiary">Bulkheads</Tag>
                <Tag tone="science">Medical</Tag>
            </>,
        );
        expect(screen.getByText("Bulkheads")).toHaveClass("my-tone-tertiary");
        expect(screen.getByText("Medical")).toHaveClass("my-tone-science");
    });

    it("renders the same in every theme", () => {
        expectThemeIndependent(<Tag tone="ops">Ops</Tag>);
    });
});
