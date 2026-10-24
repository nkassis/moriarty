import { expect, test, type Locator } from "@playwright/test";

// The visual check for Mycroft (NIM-41): one screenshot of /kit per theme. Update baselines only for
// an intended visual change (`pnpm e2e --update-snapshots`) and say so in the PR.

const THEMES: readonly string[] = ["standard", "yellow-alert", "red-alert", "report"];

test.use({ viewport: { width: 1440, height: 900 } });

test.beforeEach(async ({ page }) => {
    await page.goto("/kit?dialog=open");
    await page.evaluate(async () => {
        await document.fonts.ready;
    });
});

for (const theme of THEMES) {
    test(`kit renders in the ${theme} theme`, async ({ page }) => {
        const section: Locator = page.locator(`section[data-theme="${theme}"]`);
        await expect(section.getByRole("dialog", { name: "Confirm order" })).toBeVisible();
        await expect(section).toHaveScreenshot(`kit-${theme}.png`, {
            animations: "disabled",
            caret: "hide",
        });
    });
}

test("the tool-line toggle hides and shows tool calls", async ({ page }) => {
    const section: Locator = page.locator('section[data-theme="standard"]');
    const comms: Locator = section.getByRole("region", { name: "Comms" });
    await expect(comms.locator(".my-comm-tool")).toHaveCount(3);
    await comms.getByRole("button", { name: "Hide tool lines" }).click();
    await expect(comms.locator(".my-comm-tool")).toHaveCount(0);
    await comms.getByRole("button", { name: "Show tool lines" }).click();
    await expect(comms.locator(".my-comm-tool")).toHaveCount(3);
});
