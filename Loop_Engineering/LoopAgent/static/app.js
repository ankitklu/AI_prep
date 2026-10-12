// Loop Agent UI — calls POST /api/run, then replays the returned events
// on the agent graph so the writer → reviewer → reviser loop is visible.

const API_URL = "/api/run";

const $ = (sel) => document.querySelector(sel);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const els = {
  form: $("#form"),
  topic: $("#topic"),
  chips: $("#chips"),
  stage: $("#stage"),
  timeline: $("#timeline"),
  skeletons: $("#skeletons"),
  statusText: $("#statusText"),
  particle: $("#particle"),
  replayBtn: $("#replayBtn"),
  final: $("#final"),
  finalTopic: $("#finalTopic"),
  finalText: $("#finalText"),
  finalBadge: $("#finalBadge"),
  copyBtn: $("#copyBtn"),
  wordCount: $("#wordCount"),
  meterFill: $("#meterFill"),
  meterPin: $("#meterPin"),
  modelText: $("#modelText"),
  footModel: $("#footModel"),
  stat: {
    revisions: $("#statRevisions"),
    decision: $("#statDecision"),
    steps: $("#statSteps"),
    time: $("#statTime"),
  },
  toast: $("#toast"),
};

const ICONS = {
  writer: '<svg viewBox="0 0 24 24"><path d="M4 20h4L19 9l-4-4L4 16v4zM14 6l4 4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  reviewer: '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M20 20l-4.2-4.2M8.5 11l1.8 1.8 3.4-3.6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  reviser: '<svg viewBox="0 0 24 24"><path d="M20 12a8 8 0 1 1-2.3-5.6M20 4v4.5h-4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
};

const LOADING_LINES = [
  "Writer is drafting…",
  "Reviewer is checking the rules…",
  "Reviser is polishing…",
  "Looping until it passes…",
];

let lastResult = null;
let runToken = 0; // invalidates an in-progress replay when a new one starts
let elapsed = 0;

/* ---------------- Helpers ---------------- */

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// Tiny, safe markdown: escape first, then bold / italic / code / lists / paragraphs.
function renderMarkdown(src = "") {
  const inline = (t) =>
    escapeHtml(t)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>");

  return src
    .trim()
    .split(/\n{2,}/)
    .map((block) => {
      const lines = block.split("\n");
      if (lines.every((l) => /^\s*[-*•]\s+/.test(l))) {
        return "<ul>" + lines.map((l) => `<li>${inline(l.replace(/^\s*[-*•]\s+/, ""))}</li>`).join("") + "</ul>";
      }
      if (lines.every((l) => /^\s*\d+[.)]\s+/.test(l))) {
        return "<ol>" + lines.map((l) => `<li>${inline(l.replace(/^\s*\d+[.)]\s+/, ""))}</li>`).join("") + "</ol>";
      }
      const heading = block.match(/^#{1,6}\s+(.*)$/);
      if (heading && lines.length === 1) return `<p><strong>${inline(heading[1])}</strong></p>`;
      return `<p>${lines.map(inline).join("<br>")}</p>`;
    })
    .join("");
}

const countWords = (s = "") => (s.trim().match(/\S+/g) || []).length;

function toast(msg, type = "") {
  els.toast.textContent = msg;
  els.toast.className = `toast show ${type}`;
  clearTimeout(toast._t);
  toast._t = setTimeout(() => (els.toast.className = "toast"), 3800);
}

function setStatus(text) {
  els.statusText.textContent = text;
}

function popValue(el, value, cls = "") {
  el.textContent = value;
  el.className = `stat-value ${cls}`;
  void el.offsetWidth; // restart animation
  el.classList.add("pop");
}

/* ---------------- Graph animation ---------------- */

const node = (id) => document.getElementById(`n-${id}`);
const edge = (from, to) => document.getElementById(`e-${from}-${to}`);

function resetGraph() {
  document.querySelectorAll(".node, .terminal").forEach((n) => n.classList.remove("active", "visited", "lit"));
  document.querySelectorAll(".edge").forEach((e) => e.classList.remove("active", "visited"));
  els.particle.classList.remove("on");
}

function travel(path, duration = 750) {
  if (!path) return Promise.resolve();
  if (reducedMotion) return Promise.resolve();
  const len = path.getTotalLength();
  const p = els.particle;
  p.classList.add("on");
  return new Promise((resolve) => {
    const t0 = performance.now();
    const frame = (now) => {
      const t = Math.min(1, (now - t0) / duration);
      const eased = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
      const pt = path.getPointAtLength(eased * len);
      p.setAttribute("cx", pt.x);
      p.setAttribute("cy", pt.y);
      t < 1 ? requestAnimationFrame(frame) : resolve();
    };
    requestAnimationFrame(frame);
  });
}

async function moveAlong(from, to) {
  const e = edge(from, to);
  document.querySelectorAll(".node.active").forEach((n) => {
    n.classList.remove("active");
    n.classList.add("visited");
  });
  if (e) e.classList.add("active");
  await travel(e);
  if (e) {
    e.classList.remove("active");
    e.classList.add("visited");
  }
  const target = node(to);
  if (target) target.classList.add(to === "end" || to === "start" ? "lit" : "active");
}

/* ---------------- Timeline ---------------- */

function stepCard(ev, index) {
  const li = document.createElement("li");
  li.className = "step";
  li.dataset.agent = ev.agent;

  let body = "";
  if (ev.agent === "reviewer") {
    const pass = ev.decision === "PASS";
    const feedback = ev.feedback?.trim() || (pass ? "Meets every rule. No changes needed." : "Needs another pass.");
    body = `
      <div class="step-meta">
        <span class="step-name">${ev.agent}</span>
        <span class="badge ${pass ? "pass" : "revise"}">${escapeHtml(ev.decision || "—")}</span>
        <span class="step-idx">step ${index + 1}</span>
      </div>
      <div class="step-text short">${renderMarkdown(feedback)}</div>`;
  } else {
    const label = ev.agent === "reviser" ? `revision ${ev.revision_count}` : "first draft";
    body = `
      <div class="step-meta">
        <span class="step-name">${ev.agent}</span>
        <span class="step-idx">${label} · ${countWords(ev.draft)} words · step ${index + 1}</span>
      </div>
      <div class="step-text">${renderMarkdown(ev.draft)}</div>
      <button class="expand" type="button">Show more ↓</button>`;
  }

  li.innerHTML = `<div class="step-icon">${ICONS[ev.agent] || ICONS.writer}</div><div class="step-body">${body}</div>`;

  const text = li.querySelector(".step-text");
  const btn = li.querySelector(".expand");
  if (btn) {
    btn.addEventListener("click", () => {
      const open = text.classList.toggle("open");
      btn.textContent = open ? "Show less ↑" : "Show more ↓";
    });
  }
  return li;
}

function fitExpanders() {
  // hide "show more" when the text already fits
  els.timeline.querySelectorAll(".step").forEach((li) => {
    const text = li.querySelector(".step-text");
    const btn = li.querySelector(".expand");
    if (btn && text.scrollHeight <= text.clientHeight + 4) {
      btn.remove();
      text.classList.add("short");
    }
  });
}

/* ---------------- Final answer ---------------- */

// Wrap every word in a span so it can fade in with a stagger.
function staggerWords(container) {
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  let i = 0;
  const step = Math.max(6, Math.min(22, 2400 / Math.max(1, countWords(container.textContent))));
  nodes.forEach((n) => {
    const frag = document.createDocumentFragment();
    n.textContent.split(/(\s+)/).forEach((part) => {
      if (!part) return;
      if (/^\s+$/.test(part)) return frag.appendChild(document.createTextNode(part));
      const s = document.createElement("span");
      s.className = "w";
      s.style.animationDelay = `${i++ * step}ms`;
      s.textContent = part;
      frag.appendChild(s);
    });
    n.replaceWith(frag);
  });
}

function showFinal(result) {
  const pass = result.final_decision === "PASS";
  els.finalTopic.textContent = result.topic;
  els.finalBadge.textContent = pass ? "PASS" : "BEST EFFORT";
  els.finalBadge.className = `badge ${pass ? "pass" : "revise"}`;
  els.finalText.innerHTML = renderMarkdown(result.final_answer);
  if (!reducedMotion) staggerWords(els.finalText);

  els.final.hidden = false;
  requestAnimationFrame(() => els.final.scrollIntoView({ behavior: "smooth", block: "start" }));

  const words = countWords(result.final_answer);
  const pct = Math.min(100, (words / 220) * 100);
  els.meterFill.style.width = "0%";
  els.meterPin.style.left = "0%";
  animateNumber(els.wordCount, words, 1400);
  setTimeout(() => {
    els.meterFill.style.width = `${pct}%`;
    els.meterPin.style.left = `${pct}%`;
  }, 250);

  if (pass) setTimeout(() => burst(els.finalBadge), 400);
}

function animateNumber(el, to, duration) {
  const t0 = performance.now();
  const frame = (now) => {
    const t = Math.min(1, (now - t0) / duration);
    el.textContent = Math.round(to * (1 - Math.pow(1 - t, 3)));
    if (t < 1) requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
}

function burst(anchor) {
  if (reducedMotion) return;
  const r = anchor.getBoundingClientRect();
  const colors = ["#a78bfa", "#22d3ee", "#f472b6", "#34d399", "#fbbf24"];
  for (let i = 0; i < 36; i++) {
    const s = document.createElement("span");
    s.className = "spark";
    const angle = Math.random() * Math.PI * 2;
    const dist = 60 + Math.random() * 120;
    s.style.left = `${r.left + r.width / 2}px`;
    s.style.top = `${r.top + r.height / 2}px`;
    s.style.background = colors[i % colors.length];
    s.style.setProperty("--x", `${Math.cos(angle) * dist}px`);
    s.style.setProperty("--y", `${Math.sin(angle) * dist + 40}px`);
    s.style.setProperty("--r", `${Math.random() * 720 - 360}deg`);
    document.body.appendChild(s);
    setTimeout(() => s.remove(), 1400);
  }
}

/* ---------------- Replay ---------------- */

async function replay(result) {
  const token = ++runToken;
  const alive = () => token === runToken;

  document.body.classList.remove("done");
  document.body.classList.add("replaying");
  els.replayBtn.hidden = true;
  els.final.hidden = true;
  els.timeline.innerHTML = "";
  els.timeline.style.setProperty("--progress", 0);
  els.skeletons.hidden = true;
  resetGraph();
  popValue(els.stat.revisions, 0);
  popValue(els.stat.decision, "—");
  popValue(els.stat.steps, 0);

  node("start").classList.add("lit");
  const events = result.events || [];
  let prev = "start";
  let pause = reducedMotion ? 0 : 650;

  for (let i = 0; i < events.length; i++) {
    if (!alive()) return;
    const ev = events[i];
    setStatus(`${ev.agent[0].toUpperCase() + ev.agent.slice(1)} running`);
    await moveAlong(prev, ev.agent);
    if (!alive()) return;

    els.timeline.appendChild(stepCard(ev, i));
    els.timeline.style.setProperty("--progress", (i + 1) / events.length);
    popValue(els.stat.steps, i + 1);
    if (ev.agent === "reviser") popValue(els.stat.revisions, ev.revision_count);
    if (ev.agent === "reviewer") {
      popValue(els.stat.decision, ev.decision || "—", ev.decision === "PASS" ? "pass" : "revise");
    }
    fitExpanders();
    prev = ev.agent;
    await sleep(pause);
  }

  if (!alive()) return;
  setStatus("Finishing");
  await moveAlong(prev, "end");
  els.particle.classList.remove("on");

  document.body.classList.remove("replaying");
  document.body.classList.add("done");
  setStatus(`Done in ${elapsed.toFixed(1)}s`);
  popValue(els.stat.revisions, result.revision_count ?? 0);
  els.replayBtn.hidden = false;
  showFinal(result);
}

/* ---------------- Run ---------------- */

async function run(topic) {
  topic = topic.trim();
  if (!topic) {
    els.topic.focus();
    toast("Type a topic first ✨");
    return;
  }
  if (document.body.classList.contains("loading")) return;

  runToken++; // stop any running replay
  document.body.classList.add("loading", "has-run");
  document.body.classList.remove("done", "replaying");
  els.stage.hidden = false;
  els.final.hidden = true;
  els.replayBtn.hidden = true;
  els.timeline.innerHTML = "";
  els.skeletons.hidden = false;
  resetGraph();
  ["revisions", "steps"].forEach((k) => popValue(els.stat[k], 0));
  popValue(els.stat.decision, "—");
  els.stage.scrollIntoView({ behavior: "smooth", block: "start" });

  let line = 0;
  setStatus(LOADING_LINES[0]);
  const lineTimer = setInterval(() => setStatus(LOADING_LINES[++line % LOADING_LINES.length]), 2200);
  const t0 = performance.now();
  const clock = setInterval(() => (els.stat.time.textContent = `${((performance.now() - t0) / 1000).toFixed(1)}s`), 100);

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    });
    if (!res.ok) {
      let detail = `${res.status} ${res.statusText}`;
      try {
        const j = await res.json();
        detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail ?? j);
      } catch {}
      throw new Error(detail);
    }
    const result = await res.json();
    elapsed = (performance.now() - t0) / 1000;
    lastResult = result;

    if (result.model) {
      els.modelText.textContent = `${result.provider || "Groq"} · ${result.model}`;
      els.footModel.textContent = result.model;
    }

    clearInterval(lineTimer);
    clearInterval(clock);
    els.stat.time.textContent = `${elapsed.toFixed(1)}s`;
    document.body.classList.remove("loading");
    await replay(result);
  } catch (err) {
    clearInterval(lineTimer);
    clearInterval(clock);
    document.body.classList.remove("loading");
    els.skeletons.hidden = true;
    setStatus("Error");
    toast(`Something went wrong: ${err.message}`, "error");
    console.error(err);
  }
}

/* ---------------- Wiring ---------------- */

els.form.addEventListener("submit", (e) => {
  e.preventDefault();
  run(els.topic.value);
});

els.topic.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    run(els.topic.value);
  }
});

// auto-grow textarea
els.topic.addEventListener("input", () => {
  els.topic.style.height = "auto";
  els.topic.style.height = `${els.topic.scrollHeight}px`;
});

els.chips.addEventListener("click", (e) => {
  const chip = e.target.closest(".chip");
  if (!chip) return;
  els.topic.value = chip.textContent;
  els.topic.dispatchEvent(new Event("input"));
  run(chip.textContent);
});

els.replayBtn.addEventListener("click", () => lastResult && replay(lastResult));

els.copyBtn.addEventListener("click", async () => {
  if (!lastResult) return;
  try {
    await navigator.clipboard.writeText(lastResult.final_answer);
    els.copyBtn.querySelector("span").textContent = "Copied";
    setTimeout(() => (els.copyBtn.querySelector("span").textContent = "Copy"), 1600);
  } catch {
    toast("Couldn't access the clipboard", "error");
  }
});

// cursor spotlight on cards
document.addEventListener("pointermove", (e) => {
  document.querySelectorAll(".glow-card").forEach((card) => {
    const r = card.getBoundingClientRect();
    card.style.setProperty("--mx", `${e.clientX - r.left}px`);
    card.style.setProperty("--my", `${e.clientY - r.top}px`);
  });
});

els.topic.focus();
