import { StrictMode, type ReactElement } from "react";
import { createRoot } from "react-dom/client";
import { Kit } from "./kit/Kit";

function Page(): ReactElement {
    // Plain path switch until the bridge screens arrive with TanStack Router.
    if (window.location.pathname === "/kit") {
        const dialogOpen: boolean =
            new URLSearchParams(window.location.search).get("dialog") === "open";
        return <Kit dialogOpen={dialogOpen} />;
    }
    return (
        <main>
            <a href="/kit">Mycroft kit</a>
        </main>
    );
}

const root: HTMLElement | null = document.getElementById("root");
if (root === null) throw new Error("#root is missing from index.html");

createRoot(root).render(
    <StrictMode>
        <Page />
    </StrictMode>,
);
