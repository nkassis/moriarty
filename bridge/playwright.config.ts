import { defineConfig, devices } from "@playwright/test";

const PORT: number = 4173;

export default defineConfig({
    testDir: "test/e2e",
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    reporter: "list",
    use: {
        baseURL: `http://localhost:${String(PORT)}`,
        // Cascade animates unless motion is reduced; screenshots need a still frame.
        reducedMotion: "reduce",
    },
    projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
    webServer: {
        command: `pnpm build && pnpm preview --port ${String(PORT)} --strictPort`,
        port: PORT,
        reuseExistingServer: !process.env.CI,
    },
});
