import { useState, type ReactElement } from "react";
import {
    AgentCard,
    AlertBanner,
    Button,
    Cascade,
    Dialog,
    Frame,
    Gauge,
    Readout,
    Status,
    Tag,
    type RailId,
    type ThemeId,
} from "../mycroft";
import { KitCommVariants, KitComms } from "./KitComms";
import { KitIncidents } from "./KitIncidents";
import { CREW, NAV } from "./sample";

export interface ThemeSectionProps {
    theme: ThemeId;
    name: string;
    dialogOpen: boolean;
}

/** Every Mycroft component, composed as on the live artboard, under one data-theme. */
export function ThemeSection({ theme, name, dialogOpen }: ThemeSectionProps): ReactElement {
    const [screen, setScreen] = useState<RailId>("bridge");
    const [crewPick, setCrewPick] = useState<string>("Ops");
    const [confirm, setConfirm] = useState<boolean>(dialogOpen);
    const headingId: string = `kit-${theme}`;
    return (
        <section data-theme={theme} className="kit-theme" aria-labelledby={headingId}>
            <h2 id={headingId} className="type-heading kit-theme-name">
                {name}
            </h2>

            <Frame
                title="Moriarty"
                quiet={false}
                rail={{ items: NAV, selected: screen, onSelect: setScreen, label: "Screens" }}
            >
                <div className="kit-readouts">
                    <Readout label="Ship time" value="00:04:12" />
                    <Readout label="Open incidents" value="2" tone="secondary" />
                    <Readout label="Awaiting captain" value="1" tone="accent" />
                    <Readout label="Budget used" value="41" unit="%" level={0.41} tone="quiet" />
                </div>
                <div className="kit-row">
                    <Button>Make it so</Button>
                    <Button tone="secondary">Send to all</Button>
                    <Button tone="tertiary">Tertiary</Button>
                    <Button tone="accent" index="07">
                        Accent
                    </Button>
                    <Button tone="quiet" shape="block">
                        Belay
                    </Button>
                    <Button disabled>Disabled</Button>
                </div>
                <div className="kit-row">
                    <Status level="ok" />
                    <Status level="warn" />
                    <Status level="crit" />
                    <Status level="info" />
                    <Status level="info">Queued</Status>
                </div>
                <div className="kit-row">
                    <Tag>Sensors</Tag>
                    <Tag tone="tertiary">Bulkheads</Tag>
                    <Tag tone="command">Captain</Tag>
                    <Tag tone="ops">Ops 02</Tag>
                    <Tag tone="science">Science 04</Tag>
                </div>
            </Frame>

            <AlertBanner
                condition="yellow"
                detail="Unlisted lifeform on deck 7 · contagion spreading on the same deck · seal order pending"
            />
            <AlertBanner
                condition="red"
                detail="Hull breach, deck 4"
                onStandDown={() => undefined}
            />

            <div className="kit-grid">
                <KitComms />
                <KitIncidents />
                <div className="kit-stack">
                    <Frame title="Captain's chair" tone="accent">
                        <p className="kit-strong">Seal deck 7, sections 10 to 16</p>
                        <p className="type-caption kit-muted">
                            SEC 03 · INC-0042 · 00:04:11 · authorizes BULKHEADS.seal_section(deck=7,
                            sections=10..16)
                        </p>
                        <div className="kit-row">
                            <Button
                                onClick={() => {
                                    setConfirm(true);
                                }}
                            >
                                Make it so
                            </Button>
                            <Button tone="quiet">Belay</Button>
                        </div>
                    </Frame>
                    <Frame title="Budget" tone="tertiary">
                        <div className="kit-row kit-top">
                            <Gauge
                                label="INC-0042 used"
                                level={0.31}
                                value="31 %"
                                warn={0.7}
                                crit={0.9}
                                height={110}
                            />
                            <Gauge
                                label="INC-0043 used"
                                level={0.58}
                                value="58 %"
                                warn={0.7}
                                crit={0.9}
                                height={110}
                            />
                            <Gauge
                                label="INC-0044 used"
                                level={0.76}
                                value="76 %"
                                warn={0.7}
                                crit={0.9}
                                height={110}
                            />
                            <Gauge
                                label="INC-0045 used"
                                level={0.94}
                                value="94 %"
                                warn={0.7}
                                crit={0.9}
                                height={110}
                            />
                            <div className="kit-stack kit-grow">
                                <Readout label="Tokens, run" value="41 280" />
                                <Readout
                                    label="Cost, run"
                                    value="0.07"
                                    unit="USD"
                                    tone="secondary"
                                />
                                <Readout label="Model" value="qwen-3.7-14b" />
                            </div>
                        </div>
                    </Frame>
                </div>
            </div>

            <Frame title="Crew" tone="secondary" index="06">
                <div className="kit-crew">
                    {CREW.map((agent) => (
                        <AgentCard
                            key={agent.name}
                            {...agent}
                            selected={crewPick === agent.name}
                            onClick={() => {
                                setCrewPick(agent.name);
                            }}
                        />
                    ))}
                </div>
                <div className="kit-row">
                    <Cascade state="idle" />
                    <Cascade state="thinking" tone="science" />
                    <Cascade state="acting" tone="command" />
                    <Cascade state="standby" />
                </div>
            </Frame>

            <div className="kit-grid kit-grid-2">
                <KitCommVariants />
                <Frame title="Dialog" tone="quiet">
                    <div className="kit-dialog-box">
                        <Button
                            tone="secondary"
                            onClick={() => {
                                setConfirm(true);
                            }}
                        >
                            Show dialog
                        </Button>
                        <Dialog
                            open={confirm}
                            level="warn"
                            title="Confirm order"
                            onClose={() => {
                                setConfirm(false);
                            }}
                            actions={
                                <>
                                    <Button
                                        tone="quiet"
                                        onClick={() => {
                                            setConfirm(false);
                                        }}
                                    >
                                        Cancel
                                    </Button>
                                    <Button
                                        onClick={() => {
                                            setConfirm(false);
                                        }}
                                    >
                                        Confirm
                                    </Button>
                                </>
                            }
                        >
                            Issue order ORD-0007 authorizing BULKHEADS.seal_section(deck=7,
                            sections=10..16) for INC-0042. Lifts stay restricted; Team 2 holds at
                            the lift. The order posts to the incident channel and is logged with
                            this decision record.
                        </Dialog>
                    </div>
                </Frame>
            </div>
        </section>
    );
}
