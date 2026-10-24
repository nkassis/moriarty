/* @ds-bundle: {"format":4,"namespace":"Mycroft","components":[{"name":"Frame"},{"name":"Rail"},{"name":"Button"},{"name":"Readout"},{"name":"Gauge"},{"name":"Status"},{"name":"Table"},{"name":"Timeline"},{"name":"CommLine"},{"name":"AgentCard"},{"name":"Cascade"},{"name":"AlertBanner"},{"name":"Dialog"}]} */
var Mycroft = (() => {
  var __create = Object.create;
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __getProtoOf = Object.getPrototypeOf;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __commonJS = (cb, mod) => function __require() {
    return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
  };
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
    // If the importer is in node compatibility mode or this is not an ESM
    // file that has been converted to a CommonJS file using a Babel-
    // compatible transform (i.e. "__esModule" has not been set), then set
    // "default" to the CommonJS "module.exports" for node compatibility.
    isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
    mod
  ));
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // shim/react.js
  var require_react = __commonJS({
    "shim/react.js"(exports, module) {
      module.exports = window.React;
    }
  });

  // ../mycroft/project/components/src/index.tsx
  var src_exports = {};
  __export(src_exports, {
    AgentCard: () => AgentCard,
    AlertBanner: () => AlertBanner,
    Button: () => Button,
    Cascade: () => Cascade,
    CommLine: () => CommLine,
    Dialog: () => Dialog,
    Frame: () => Frame,
    Gauge: () => Gauge,
    Rail: () => Rail,
    Readout: () => Readout,
    Status: () => Status,
    Table: () => Table,
    Timeline: () => Timeline
  });

  // ../mycroft/project/components/src/structure.tsx
  var React2 = __toESM(require_react());

  // ../mycroft/project/components/src/shared.tsx
  var React = __toESM(require_react());
  var TONES = { primary: true, secondary: true, tertiary: true, quiet: true, accent: true, command: true, ops: true, science: true };
  var DIVISIONS = { command: true, ops: true, science: true };
  function toneClass(tone, fallback) {
    return "my-tone-" + (tone && TONES[tone] ? tone : fallback);
  }
  function cx(...parts) {
    return parts.filter(Boolean).join(" ");
  }
  function useReducedMotion() {
    const get = () => typeof window !== "undefined" && !!window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const [reduced, setReduced] = React.useState(get);
    React.useEffect(() => {
      if (typeof window === "undefined" || !window.matchMedia) return;
      const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
      const on = () => setReduced(mq.matches);
      mq.addEventListener ? mq.addEventListener("change", on) : mq.addListener(on);
      return () => {
        mq.removeEventListener ? mq.removeEventListener("change", on) : mq.removeListener(on);
      };
    }, []);
    return reduced;
  }

  // ../mycroft/project/components/src/structure.tsx
  function Button({ tone, shape, index, className, children, type, ...rest }) {
    return /* @__PURE__ */ React2.createElement("button", { ...rest, type: type || "button", className: cx("my-btn", shape === "block" && "my-btn-block", toneClass(tone, "primary"), className) }, /* @__PURE__ */ React2.createElement("span", { className: "my-btn-label" }, children), index != null ? /* @__PURE__ */ React2.createElement("span", { className: "my-btn-index" }, index) : null);
  }
  var RAIL_DEFAULTS = ["primary", "secondary", "tertiary", "quiet"];
  function Rail({ items, selected, onSelect, label, className }) {
    return /* @__PURE__ */ React2.createElement("nav", { className: cx("my-rail", className), "aria-label": label || "Rail" }, items.map((it, i) => {
      const id = it.id != null ? it.id : i;
      const isSel = selected != null && selected === id;
      const size = it.size || (i === items.length - 1 ? "fill" : "md");
      return /* @__PURE__ */ React2.createElement(
        "button",
        {
          key: String(id),
          type: "button",
          className: cx("my-rail-seg", size === "tall" && "my-rail-seg-tall", size === "fill" && "my-rail-seg-fill", isSel && "my-rail-seg-selected", toneClass(it.tone, RAIL_DEFAULTS[i % RAIL_DEFAULTS.length])),
          "aria-current": isSel ? "true" : void 0,
          onClick: onSelect ? () => onSelect(id, it) : void 0
        },
        /* @__PURE__ */ React2.createElement("span", null, it.label),
        it.index != null ? /* @__PURE__ */ React2.createElement("span", { className: "my-rail-index" }, it.index) : null
      );
    }));
  }
  function Frame({ title, index, tone, quiet = true, rail, footer, children, className }) {
    const t = toneClass(tone, "primary");
    const label = typeof title === "string" ? title : void 0;
    if (quiet) {
      return /* @__PURE__ */ React2.createElement("section", { className: cx("my-frame my-frame-quiet", t, className), "aria-label": label }, /* @__PURE__ */ React2.createElement("div", { className: "my-frame-titlebar" }, title ? /* @__PURE__ */ React2.createElement("h2", { className: "my-frame-quiet-title" }, title, index != null ? /* @__PURE__ */ React2.createElement("span", { className: "my-frame-quiet-index" }, index) : null) : null), /* @__PURE__ */ React2.createElement("div", { className: "my-frame-well" }, children));
    }
    const railNode = rail ? React2.isValidElement(rail) ? rail : /* @__PURE__ */ React2.createElement(Rail, { ...rail }) : null;
    return /* @__PURE__ */ React2.createElement("section", { className: cx("my-frame my-frame-elbow", footer && "my-frame-footer", className), "aria-label": label }, /* @__PURE__ */ React2.createElement("div", { className: cx("my-elbow", t) }), /* @__PURE__ */ React2.createElement("div", { className: "my-frame-head" }, /* @__PURE__ */ React2.createElement("div", { className: cx("my-frame-bar", t) }), title ? /* @__PURE__ */ React2.createElement("h2", { className: cx("my-frame-title", t) }, title, index != null ? /* @__PURE__ */ React2.createElement("span", { className: "my-frame-title-index" }, index) : null) : null), /* @__PURE__ */ React2.createElement("div", { className: "my-frame-rail" }, railNode), /* @__PURE__ */ React2.createElement("div", { className: "my-frame-well" }, children), footer ? /* @__PURE__ */ React2.createElement("div", { className: cx("my-elbow my-elbow-bottom", t) }) : null, footer ? /* @__PURE__ */ React2.createElement("div", { className: "my-frame-foot" }, /* @__PURE__ */ React2.createElement("div", { className: cx("my-frame-bar", t) })) : null);
  }
  function Dialog({ open, title, level, tone, children, actions, onClose, className }) {
    const ref = React2.useRef(null);
    React2.useEffect(() => {
      if (!open) return;
      const el = ref.current;
      const first = el && el.querySelector("button, [href], input, [tabindex]:not([tabindex='-1'])");
      first && first.focus();
      const onKey = (e) => {
        if (e.key === "Escape" && onClose) onClose();
      };
      document.addEventListener("keydown", onKey);
      return () => document.removeEventListener("keydown", onKey);
    }, [open, onClose]);
    if (!open) return null;
    const t = level === "crit" ? "my-level-crit" : level === "warn" ? "my-level-warn" : toneClass(tone, "primary");
    return /* @__PURE__ */ React2.createElement("div", { className: "my-dialog-scrim", onClick: onClose }, /* @__PURE__ */ React2.createElement("div", { ref, role: "dialog", "aria-modal": "true", "aria-label": typeof title === "string" ? title : void 0, className: cx("my-dialog", t, className), onClick: (e) => e.stopPropagation() }, /* @__PURE__ */ React2.createElement("div", { className: "my-dialog-elbow" }), /* @__PURE__ */ React2.createElement("div", { className: "my-dialog-bar" }), /* @__PURE__ */ React2.createElement("div", { className: "my-dialog-body" }, /* @__PURE__ */ React2.createElement("h2", { className: "my-dialog-title" }, title), /* @__PURE__ */ React2.createElement("div", { className: "my-dialog-text" }, children), actions ? /* @__PURE__ */ React2.createElement("div", { className: "my-dialog-actions" }, actions) : null), /* @__PURE__ */ React2.createElement("div", { className: "my-dialog-foot" })));
  }
  function AlertBanner({ condition, children, detail, setTheme, onStandDown, className }) {
    React2.useEffect(() => {
      if (!setTheme || typeof document === "undefined") return;
      const html = document.documentElement;
      const prev = html.getAttribute("data-theme");
      html.setAttribute("data-theme", condition === "red" ? "red-alert" : "yellow-alert");
      return () => {
        prev == null ? html.removeAttribute("data-theme") : html.setAttribute("data-theme", prev);
      };
    }, [condition, setTheme]);
    const word = children || (condition === "red" ? "Red alert" : "Condition yellow");
    return /* @__PURE__ */ React2.createElement("div", { role: "alert", className: cx("my-alert", condition === "red" ? "my-alert-red" : "my-alert-yellow", className) }, /* @__PURE__ */ React2.createElement("div", { className: "my-alert-cap" }), /* @__PURE__ */ React2.createElement("div", { className: "my-alert-word" }, word), detail ? /* @__PURE__ */ React2.createElement("div", { className: "my-alert-detail" }, detail) : null, onStandDown ? /* @__PURE__ */ React2.createElement("button", { type: "button", className: "my-alert-stand", onClick: onStandDown }, "Stand down") : null);
  }

  // ../mycroft/project/components/src/data.tsx
  var React3 = __toESM(require_react());
  function Readout({ label, value, unit, level, tone, className }) {
    let meter = null;
    if (typeof level === "number") {
      const on = Math.max(0, Math.min(10, Math.round(level * 10)));
      const cells = [];
      for (let i = 0; i < 10; i++) cells.push(/* @__PURE__ */ React3.createElement("span", { key: i, className: i < on ? "on" : "" }));
      meter = /* @__PURE__ */ React3.createElement("div", { className: "my-readout-meter", role: "meter", "aria-valuemin": 0, "aria-valuemax": 1, "aria-valuenow": level, "aria-label": typeof label === "string" ? label : void 0 }, cells);
    }
    return /* @__PURE__ */ React3.createElement("div", { className: cx("my-readout", toneClass(tone, "primary"), className) }, /* @__PURE__ */ React3.createElement("span", { className: "my-readout-label" }, label), /* @__PURE__ */ React3.createElement("span", { className: "my-readout-leader", "aria-hidden": "true" }), /* @__PURE__ */ React3.createElement("span", { className: "my-readout-value" }, value, unit ? /* @__PURE__ */ React3.createElement("span", { className: "my-readout-unit" }, unit) : null), meter);
  }
  function Gauge({ label, level, value, segments = 20, warn, crit, tone, height = 160, className }) {
    const n = Math.max(4, Math.min(60, segments));
    const on = Math.max(0, Math.min(n, Math.round(level * n)));
    const state = typeof crit === "number" && level >= crit ? "crit" : typeof warn === "number" && level >= warn ? "warn" : "";
    const cells = [];
    for (let i = n - 1; i >= 0; i--) {
      const frac = (i + 1) / n;
      const lit = i < on;
      const zone = typeof crit === "number" && frac > crit ? "z-crit" : typeof warn === "number" && frac > warn ? "z-warn" : "";
      cells.push(/* @__PURE__ */ React3.createElement("span", { key: i, className: cx(lit && "on", zone) }));
    }
    return /* @__PURE__ */ React3.createElement("div", { className: cx("my-gauge", toneClass(tone, "primary"), state && "my-gauge-" + state, className), role: "meter", "aria-valuemin": 0, "aria-valuemax": 1, "aria-valuenow": level, "aria-label": typeof label === "string" ? label : void 0 }, /* @__PURE__ */ React3.createElement("div", { className: "my-gauge-bar", style: { height } }, cells), /* @__PURE__ */ React3.createElement("div", { className: "my-gauge-label" }, label), value != null ? /* @__PURE__ */ React3.createElement("div", { className: "my-gauge-value" }, value) : null);
  }
  var WORDS = { ok: "Nominal", warn: "Degraded", crit: "Critical", info: "Standby" };
  function Status({ level, children, className }) {
    const l = WORDS[level] ? level : "info";
    return /* @__PURE__ */ React3.createElement("span", { className: cx("my-status", "my-status-" + l, className), role: "status" }, children || WORDS[l]);
  }
  function Table({ columns, rows, rowKey, tone, caption, selected, onSelect, className }) {
    return /* @__PURE__ */ React3.createElement("table", { className: cx("my-table", toneClass(tone, "primary"), className) }, caption ? /* @__PURE__ */ React3.createElement("caption", { className: "my-table-caption" }, caption) : null, /* @__PURE__ */ React3.createElement("thead", null, /* @__PURE__ */ React3.createElement("tr", null, columns.map((c) => /* @__PURE__ */ React3.createElement("th", { key: c.key, scope: "col", className: cx("my-table-th", c.kind === "num" && "num"), style: c.width != null ? { width: c.width } : void 0 }, c.header)))), /* @__PURE__ */ React3.createElement("tbody", null, rows.map((r, i) => {
      const k = rowKey ? rowKey(r, i) : i;
      const sel = selected != null && selected === k;
      return /* @__PURE__ */ React3.createElement("tr", { key: String(k), className: cx(sel && "selected", onSelect && "clickable"), "aria-selected": sel || void 0, onClick: onSelect ? () => onSelect(k, r) : void 0 }, columns.map((c) => /* @__PURE__ */ React3.createElement("td", { key: c.key, className: cx("my-table-td", c.kind === "num" && "num") }, c.cell ? c.cell(r, i) : r[c.key])));
    })));
  }
  function Timeline({ events, className }) {
    return /* @__PURE__ */ React3.createElement("ol", { className: cx("my-timeline", className) }, events.map((e, i) => /* @__PURE__ */ React3.createElement("li", { key: e.id != null ? String(e.id) : i, className: cx("my-tl-event", e.level ? "my-tl-" + e.level : toneClass(e.tone, "primary")) }, /* @__PURE__ */ React3.createElement("span", { className: "my-tl-time" }, e.time), /* @__PURE__ */ React3.createElement("span", { className: "my-tl-mark", "aria-hidden": "true" }), /* @__PURE__ */ React3.createElement("div", { className: "my-tl-body" }, /* @__PURE__ */ React3.createElement("div", { className: "my-tl-head" }, e.from ? /* @__PURE__ */ React3.createElement("span", { className: cx("my-tl-from", toneClass(e.tone, "primary")) }, e.from) : null, /* @__PURE__ */ React3.createElement("span", { className: "my-tl-title" }, e.title)), e.children ? /* @__PURE__ */ React3.createElement("div", { className: "my-tl-text" }, e.children) : null))));
  }

  // ../mycroft/project/components/src/crew.tsx
  var React4 = __toESM(require_react());
  function pad(n, w) {
    let s = String(n);
    while (s.length < w) s = "0" + s;
    return s;
  }
  function seed(r, c, t) {
    return pad((r * 7919 + c * 104729 + t * 31) % 1e4, 4);
  }
  var STATE_WORD = { idle: "Idle", thinking: "Thinking", acting: "Acting", standby: "Standby" };
  function Cascade({ state = "idle", rows = 2, cols = 3, tone, className }) {
    const reduced = useReducedMotion();
    const [tick, setTick] = React4.useState(0);
    const live = (state === "thinking" || state === "acting") && !reduced;
    React4.useEffect(() => {
      if (!live) return;
      const id = setInterval(() => setTick((t) => t + 1), state === "acting" ? 120 : 320);
      return () => clearInterval(id);
    }, [live, state]);
    const cells = [];
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const hot = live && (r * cols + c + tick) % 5 === 0;
      cells.push(/* @__PURE__ */ React4.createElement("span", { key: r + "-" + c, className: cx("my-cascade-cell", hot && "hot") }, seed(r, c, live ? tick : 0)));
    }
    return /* @__PURE__ */ React4.createElement("div", { className: cx("my-cascade", "my-cascade-" + state, toneClass(tone, "ops"), className), style: { gridTemplateColumns: `repeat(${cols}, auto)` }, role: "img", "aria-label": STATE_WORD[state] || "Idle" }, cells);
  }
  function AgentCard({ name, division = "ops", index, role, state = "idle", activity, meta, selected, onClick, className }) {
    const d = DIVISIONS[division] ? division : "ops";
    const Tag = onClick ? "button" : "div";
    const st = STATE_WORD[state] ? state : "idle";
    return /* @__PURE__ */ React4.createElement(Tag, { type: onClick ? "button" : void 0, onClick, className: cx("my-agent", "my-agent-" + st, toneClass(d, "ops"), selected && "my-agent-selected", onClick && "clickable", className), "aria-pressed": onClick ? !!selected : void 0 }, /* @__PURE__ */ React4.createElement("div", { className: "my-agent-band" }, /* @__PURE__ */ React4.createElement("span", { className: "my-agent-name" }, name, index != null ? /* @__PURE__ */ React4.createElement("span", { className: "my-agent-index" }, index) : null), /* @__PURE__ */ React4.createElement("span", { className: "my-agent-state" }, STATE_WORD[st])), /* @__PURE__ */ React4.createElement("div", { className: "my-agent-body" }, /* @__PURE__ */ React4.createElement("div", { className: "my-agent-top" }, role ? /* @__PURE__ */ React4.createElement("span", { className: "my-agent-role" }, role) : /* @__PURE__ */ React4.createElement("span", null), /* @__PURE__ */ React4.createElement(Cascade, { state: st, rows: 2, cols: 3, tone: d })), activity ? /* @__PURE__ */ React4.createElement("div", { className: "my-agent-activity" }, activity) : null, meta ? /* @__PURE__ */ React4.createElement("div", { className: "my-agent-meta" }, meta) : null));
  }
  var KIND_WORD = { message: "", tool: "Tool", finding: "Finding", decision: "Decision", system: "System" };
  function CommLine({ from, index, time, tone, division, kind = "message", call, result, compact = true, sender = "pill", children, className }) {
    const isCrew = !!(division && DIVISIONS[division]) || !!(tone && DIVISIONS[tone]);
    const chipTone = toneClass(division && DIVISIONS[division] ? division : tone, "tertiary");
    const k = KIND_WORD[kind] != null ? kind : "message";
    const edge = compact && sender === "edge";
    const body = /* @__PURE__ */ React4.createElement("div", { className: "my-comm-body" }, edge ? /* @__PURE__ */ React4.createElement("span", { className: "my-comm-name" }, from, index != null ? /* @__PURE__ */ React4.createElement("span", { className: "my-comm-index" }, " ", index) : null) : null, k !== "message" ? /* @__PURE__ */ React4.createElement("span", { className: "my-comm-kind" }, KIND_WORD[k]) : null, k === "tool" ? /* @__PURE__ */ React4.createElement("span", { className: "my-comm-toolbox" }, /* @__PURE__ */ React4.createElement("code", { className: "my-comm-call" }, call), result != null ? /* @__PURE__ */ React4.createElement("span", { className: "my-comm-result" }, result) : null, children ? /* @__PURE__ */ React4.createElement("span", { className: "my-comm-text" }, children) : null) : /* @__PURE__ */ React4.createElement("span", { className: "my-comm-text" }, children));
    return /* @__PURE__ */ React4.createElement("div", { className: cx("my-comm", compact ? "my-comm-compact" : "my-comm-wide", "my-comm-" + k, isCrew && "my-comm-crew", edge && "my-comm-edge", chipTone, className) }, edge ? null : /* @__PURE__ */ React4.createElement("span", { className: "my-comm-from", title: typeof from === "string" ? from : void 0 }, from, index != null ? /* @__PURE__ */ React4.createElement("span", { className: "my-comm-index" }, index) : null), body, /* @__PURE__ */ React4.createElement("span", { className: "my-comm-time" }, time));
  }
  return __toCommonJS(src_exports);
})();
