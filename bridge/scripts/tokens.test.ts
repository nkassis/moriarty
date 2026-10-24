// @vitest-environment node
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { buildCss, buildTs, resolveTheme, type Tokens } from "./tokens.ts";

const DESIGN: URL = new URL("../../docs/design/mycroft/", import.meta.url);
const tokens: Tokens = JSON.parse(readFileSync(new URL("tokens.json", DESIGN), "utf8")) as Tokens;

function fixture(): Tokens {
    return {
        color: {
            themes: [
                { id: "standard", name: "Standard" },
                { id: "red-alert", name: "Red alert" },
            ],
            tokens: [
                { name: "band", value: { standard: "#111111", "red-alert": "#222222" }, usage: "" },
                { name: "crew", value: { standard: "#333333" }, usage: "" },
                { name: "info", value: "{band}", usage: "" },
            ],
        },
        type: { families: {}, groups: [] },
        spacing: { tokens: [] },
        radius: { tokens: [] },
        layout: { tokens: [] },
    };
}

/** Custom properties per selector in the design session's own tokens.css. */
function designBlocks(): Map<string, Map<string, string>> {
    const css: string = readFileSync(new URL("tokens.css", DESIGN), "utf8").replace(
        /\/\*[\s\S]*?\*\//g,
        "",
    );
    const blocks: Map<string, Map<string, string>> = new Map();
    for (const m of css.matchAll(/([^{}]+)\{([^}]*)\}/g)) {
        const decls: Map<string, string> = new Map();
        for (const d of (m[2] ?? "").matchAll(/--([a-z0-9-]+):\s*([^;]+);/g)) {
            decls.set(d[1] ?? "", (d[2] ?? "").trim());
        }
        blocks.set((m[1] ?? "").trim(), decls);
    }
    return blocks;
}

describe("resolveTheme", () => {
    it("fills a theme's missing value from standard", () => {
        expect(resolveTheme(fixture(), "red-alert").get("crew")).toEqual({
            css: "#333333",
            resolved: "#333333",
        });
    });

    it("re-declares an alias in every theme and resolves it per theme", () => {
        expect(resolveTheme(fixture(), "standard").get("info")).toEqual({
            css: "var(--band)",
            resolved: "#111111",
        });
        expect(resolveTheme(fixture(), "red-alert").get("info")).toEqual({
            css: "var(--band)",
            resolved: "#222222",
        });
    });

    it("rejects an unknown alias", () => {
        const t: Tokens = fixture();
        t.color.tokens.push({ name: "bad", value: "{missing}", usage: "" });
        expect(() => resolveTheme(t, "standard")).toThrow("unknown colour alias {missing}");
    });

    it("rejects a token without a standard value", () => {
        const t: Tokens = fixture();
        t.color.tokens.push({ name: "orphan", value: { "red-alert": "#444444" }, usage: "" });
        expect(() => resolveTheme(t, "standard")).toThrow("orphan has no standard value");
    });
});

describe("generated tokens.css", () => {
    it("matches every value in the design session's tokens.css", () => {
        const design: Map<string, Map<string, string>> = designBlocks();
        const root: Map<string, string> = design.get(":root") ?? new Map<string, string>();
        for (const theme of tokens.color.themes) {
            const own: Map<string, string> =
                theme.id === "standard"
                    ? new Map<string, string>()
                    : (design.get(`[data-theme="${theme.id}"]`) ?? new Map<string, string>());
            for (const [name, value] of resolveTheme(tokens, theme.id)) {
                expect(value.css, `${theme.id} --${name}`).toBe(own.get(name) ?? root.get(name));
            }
        }
        const css: string = buildCss(tokens);
        for (const [name, value] of root) {
            if (!name.startsWith("font-") && resolveTheme(tokens, "standard").has(name)) continue;
            expect(css).toContain(`--${name}: ${value};`);
        }
    });

    it("declares every colour in every theme block", () => {
        const css: string = buildCss(tokens);
        for (const theme of tokens.color.themes.filter((t) => t.id !== "standard")) {
            const block: string = css.split(`[data-theme="${theme.id}"] {`)[1]?.split("}")[0] ?? "";
            for (const token of tokens.color.tokens) expect(block).toContain(`--${token.name}:`);
        }
    });
});

describe("committed output", () => {
    it("is up to date with tokens.json", () => {
        const out: URL = new URL("../src/mycroft/", import.meta.url);
        expect(readFileSync(new URL("tokens.css", out), "utf8")).toBe(buildCss(tokens));
        expect(readFileSync(new URL("tokens.ts", out), "utf8")).toBe(buildTs(tokens));
    });
});
