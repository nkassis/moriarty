import type { ReactElement } from "react";
import { THEMES } from "../mycroft";
import { ThemeSection } from "./ThemeSection";
import "./kit.css";

export interface KitProps {
    /** Start with the Dialog open in every theme (`/kit?dialog=open`), for screenshots. */
    dialogOpen?: boolean;
}

/** /kit: every Mycroft component in every theme. The visual check for the design system. */
export function Kit({ dialogOpen = false }: KitProps): ReactElement {
    return (
        <main className="kit">
            <h1 className="type-title kit-title">Mycroft kit</h1>
            {THEMES.map((t) => (
                <ThemeSection key={t.id} theme={t.id} name={t.name} dialogOpen={dialogOpen} />
            ))}
        </main>
    );
}
