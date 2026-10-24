import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
    plugins: [react()],
    // `/kit` is served through the SPA fallback, in dev and in `vite preview`.
    appType: "spa",
});
