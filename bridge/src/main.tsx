import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

const root: HTMLElement | null = document.getElementById("root");
if (root === null) throw new Error("#root is missing from index.html");

createRoot(root).render(
    <StrictMode>
        <main>Bridge</main>
    </StrictMode>,
);
