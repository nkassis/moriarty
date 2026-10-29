# M1 decisions

Binding answers to the questions raised before M1 code was written. Where one changes the contract, `docs/architecture.md` carries it. Entries 1 to 4 answer the questions in NIM-13 and keep their numbers; numbers are never reused.

Entries are held to the bar in `.claude/rules/decision-log.md`: a competent engineer could have chosen otherwise, reversing would cost more than a day, and each entry names the alternative and the cost.

## Models and crew

### 1. The v0.1 recording runs on Claude Sonnet 5.5; Ollama stays the dev default

**Why:** The video is one take of a multi-step tool-calling run with three live stations, and a failed take costs a re-record. `profiles/demo.json` maps `triage` to `anthropic/claude-sonnet-5-5`; development and eval iteration stay on local Ollama, where runs are free.

**Instead of:** Haiku 5.5 for the recording. Cheaper per take, and the planned cheap tier for the harness, but less reliable at the sequence the episode needs on camera.

**Cost:** the video shows a stronger model than the harness will measure, each take costs money, and the demo profile needs a provider key the dev setup does not.

**Status:** Accepted.

### 2. `crew-xo` defines every station; which are live is run-profile configuration

**Why:** The bridge shows the full roster, and a crew that must route around missing stations is the realistic case. For v0.1, XO, Ops and Security are live. Science, Engineering and Medical heartbeat `standby`, render dimmed and never act, including on comms. A `request` to a standby station counts as nuisance.

**Instead of:** a three-station crew. Simpler, but the roster changes shape the first time a station is added, and routing around an absent station is never exercised.

**Cost:** three no-op stations to run and heartbeat, and prompts that must know who is live. A live station taking over a standby station's tools mid-run is parked (NIM-23).

**Status:** Accepted.

### 3. The bridge is React, Vite and TanStack from the first screen, on a React port of Mycroft

**Why:** Mycroft existed as a vanilla bundle. Building the Live screen on it and porting later writes the screen twice. The port is `bridge/src/mycroft/` (NIM-41), and the bridge reads contract types generated from the same JSON Schemas as the Ship.

**Instead of:** the vanilla bundle with hand-written DOM for v0.1, which ships the screen sooner with no frontend toolchain.

**Cost:** pnpm, Vite, Vitest and Playwright in the repo before there is a second screen, and the bridge track could not start until the port landed.

**Status:** Accepted.

### 4. Local models run in Ollama on the Windows host over Vulkan, `gpt-oss:20b` by default

**Why:** The dev GPU is a Radeon RX 9070 XT (RDNA4, gfx1201, 16 GB). Ollama supports it on Linux with ROCm 7, it is not in Ollama's Windows table, and ROCm under WSL2 is unverified. The Vulkan backend on the Windows host reaches the GPU today; WSL calls it at the host address. `gpt-oss:20b` fits 16 GB with the strongest tool calling in its class; `qwen3:14b` is the alternative.

**Instead of:** Ollama inside WSL2 on ROCm, one OS for everything but an unverified driver path.

**Cost:** the model host sits outside compose and outside Linux, so `moriarty doctor` must find and report the backend and model. If Ollama does not see the GPU, the fallback is llama.cpp's Vulkan server behind LiteLLM's OpenAI provider, a second backend to configure.

**Status:** Accepted.

## Scope and contract

### 5. M1 is a vertical slice that ships v0.1, not the horizontal contract-first plan

**Why:** One episode played end to end through crew, bridge, captain and debrief finds the contract gaps that layer-by-layer work would hit only when the layers first met at the former M5. The definition of done is a video script that runs twice from a clean clone on two seeds.

**Instead of:** contract, systems and gateway as parallel tracks, the first agent at the former M2 and the bridge at the former M5. Each layer would be finished before any two had met.

**Cost:** v0.1 has no harness, no baseline crew and no scorecard, so it shows the system working and measures nothing. Shortcuts taken for the video have to be found and paid for in M2+.

**Status:** Accepted.

### 6. M1 builds a subset of the architecture's tool names, not new short ones

**Why:** Prompts, episode `reactions` and `decoys`, and the action stream all key on tool names, and the systems table and Doyle sketch already say `seal_section`. v0.1 builds `scan_section`, `lookup_person`, `seal_section`, `unseal_section`, `dispatch_team` and `detain`.

**Instead of:** NIM-17's `sweep`, `lookup`, `seal`, `dispatch`, qualified by the system name. Fewer tokens, but every table, sketch and reaction changes, and a tool quoted alone loses its noun.

**Cost:** longer names in every tool list a model reads, and NIM-17 has to be read through this mapping.

**Status:** Accepted.
