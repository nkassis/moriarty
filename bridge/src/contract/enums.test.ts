// @vitest-environment node
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { AGENT_STATES, COMMS_KINDS, DIVISIONS } from "./enums.ts";

const vocabulary: string = readFileSync(
    new URL("../../../docs/vocabulary.md", import.meta.url),
    "utf8",
);

function vocabularyValues(thing: string): string[] {
    const row: string | undefined = vocabulary
        .split("\n")
        .find((line) => line.startsWith(`| ${thing} |`));
    if (row === undefined) throw new Error(`no row for ${thing} in docs/vocabulary.md`);
    return [...row.matchAll(/`([^`]+)`/g)].map((m) => m[1] ?? "");
}

describe("contract enums", () => {
    it.each([
        ["Agent state", AGENT_STATES],
        ["Division", DIVISIONS],
        ["Comms kind", COMMS_KINDS],
    ] as const)("%s matches docs/vocabulary.md", (thing, values) => {
        expect([...values]).toEqual(vocabularyValues(thing));
    });
});
