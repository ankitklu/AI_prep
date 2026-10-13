(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  const els = {
    form: $("#ask-form"),
    question: $("#question"),
    charCount: $("#char-count"),
    submit: $("#submit-btn"),
    reset: $("#reset-btn"),
    statusPill: $("#status-pill"),
    statusText: $("#status-text"),
    progress: $("#progress-bar"),
    totalTime: $("#total-time"),
    routeBadge: $("#route-badge"),
    finalEmpty: $("#final-empty"),
    finalAnswer: $("#final-answer"),
    draftAnswer: $("#draft-answer"),
    traceList: $("#trace-list"),
    history: $("#history"),
    clearHistory: $("#clear-history"),
    copy: $("#copy-btn"),
    toast: $("#toast"),
    themeToggle: $("#theme-toggle"),
  };

  const STEPS = ["guardrail", "router", "specialist", "reviewer"];
  const SPECIALISTS = ["technical_agent", "billing_agent", "general_agent"];
  const HISTORY_KEY = "harness.history";
  const THEME_KEY = "harness.theme";

  let source = null;
  let stepStart = 0;
  let timer = null;
  let lastResult = null;

  /* ---------- storage helpers (never throw) ---------- */
  const store = {
    get(key, fallback) {
      try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; }
    },
    set(key, value) {
      try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* ignore */ }
    },
  };

  /* ---------- theme ---------- */
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
  }
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(store.get(THEME_KEY, prefersDark ? "dark" : "light"));
  els.themeToggle.addEventListener("click", () => {
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    applyTheme(next);
    store.set(THEME_KEY, next);
  });

  /* ---------- utils ---------- */
  function renderMarkdown(text) {
    if (window.marked && window.DOMPurify) {
      return DOMPurify.sanitize(marked.parse(text || ""));
    }
    const div = document.createElement("div");
    div.textContent = text || "";
    return div.innerHTML.replace(/\n/g, "<br>");
  }

  function formatMs(ms) {
    return ms >= 1000 ? `${(ms / 1000).toFixed(2)}s` : `${ms}ms`;
  }

  let toastTimer;
  function toast(msg, isError = false) {
    els.toast.textContent = msg;
    els.toast.classList.toggle("error", isError);
    els.toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => els.toast.classList.remove("show"), 2600);
  }

  function setStatus(state, text) {
    els.statusPill.className = `status-pill ${state}`;
    els.statusText.textContent = text;
  }

  function setBusy(busy) {
    els.submit.disabled = busy;
    els.question.disabled = busy;
    els.submit.innerHTML = busy
      ? '<span class="spinner"></span><span class="btn-label">Running…</span>'
      : '<span class="btn-label">Run pipeline</span><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  }

  function nodeEl(step) {
    return $(`.node[data-node="${step}"]`);
  }

  function setProgress(fraction, error = false) {
    els.progress.style.width = `${Math.round(fraction * 100)}%`;
    els.progress.classList.toggle("error", error);
  }

  /* ---------- tabs ---------- */
  function showTab(name) {
    $$(".tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
    $$(".tab-panel").forEach((p) => p.classList.toggle("active", p.dataset.panel === name));
  }
  $$(".tab").forEach((t) => t.addEventListener("click", () => showTab(t.dataset.tab)));

  /* ---------- pipeline state ---------- */
  function resetPipeline() {
    STEPS.forEach((step) => {
      const el = nodeEl(step);
      el.className = el.className.split(" ").filter((c) => c === "node" || c === "node-branch").join(" ");
      const result = $("[data-result]", el);
      if (result) result.innerHTML = "";
      $("[data-time]", el).textContent = "";
    });
    $$(".branch").forEach((b) => b.classList.remove("selected", "dimmed"));
    setProgress(0);
    els.totalTime.textContent = "";
  }

  function activate(step) {
    const el = nodeEl(step);
    el.classList.add("active");
    stepStart = performance.now();
    clearInterval(timer);
    const timeEl = $("[data-time]", el);
    timer = setInterval(() => {
      timeEl.textContent = formatMs(Math.round(performance.now() - stepStart));
    }, 100);
  }

  function complete(step, ms, cls = "done") {
    clearInterval(timer);
    const el = nodeEl(step);
    el.classList.remove("active");
    el.classList.add(cls);
    $("[data-time]", el).textContent = formatMs(ms);
  }

  function skip(step) {
    nodeEl(step).classList.add("skipped");
  }

  function resetResult() {
    els.routeBadge.hidden = true;
    els.finalEmpty.hidden = false;
    els.finalAnswer.innerHTML = "";
    els.draftAnswer.innerHTML = '<p class="muted">No draft yet.</p>';
    els.traceList.innerHTML = '<li class="muted">No trace yet.</li>';
    lastResult = null;
  }

  function showSkeleton() {
    els.finalEmpty.hidden = true;
    els.finalAnswer.innerHTML = '<div class="skeleton"><span></span><span></span><span></span><span></span></div>';
  }

  function renderTrace(trace) {
    els.traceList.innerHTML = trace.length
      ? trace.map((t) => `<li>${t.replace(/[<>&]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[c]))}</li>`).join("")
      : '<li class="muted">No trace yet.</li>';
  }

  function setRoute(route) {
    els.routeBadge.hidden = false;
    els.routeBadge.className = `route-badge ${route}`;
    els.routeBadge.textContent = route === "blocked" ? "Blocked" : `${route} route`;
  }

  /* ---------- handling streamed steps ---------- */
  function handleStep({ node, update, trace, duration_ms }) {
    renderTrace(trace);

    if (node === "guardrail") {
      const result = $("[data-result]", nodeEl("guardrail"));
      if (update.blocked) {
        complete("guardrail", duration_ms, "blocked");
        result.innerHTML = '<span class="tag bad">Request blocked</span>';
        ["router", "specialist", "reviewer"].forEach(skip);
        setProgress(1, true);
      } else {
        complete("guardrail", duration_ms);
        result.innerHTML = '<span class="tag ok">Passed</span>';
        setProgress(0.25);
        activate("router");
      }
      return;
    }

    if (node === "router") {
      complete("router", duration_ms);
      const route = update.route || "general";
      $("[data-result]", nodeEl("router")).innerHTML = `<span class="tag">→ ${route}</span>`;
      setRoute(route);
      $$(".branch").forEach((b) => {
        const selected = b.dataset.branch === `${route}_agent`;
        b.classList.toggle("selected", selected);
        b.classList.toggle("dimmed", !selected);
      });
      setProgress(0.5);
      activate("specialist");
      return;
    }

    if (SPECIALISTS.includes(node)) {
      complete("specialist", duration_ms);
      els.draftAnswer.innerHTML = renderMarkdown(update.draft);
      setProgress(0.75);
      activate("reviewer");
      return;
    }

    if (node === "reviewer") {
      complete("reviewer", duration_ms);
      $("[data-result]", nodeEl("reviewer")).innerHTML = '<span class="tag ok">Approved</span>';
      setProgress(1);
    }
  }

  function handleDone(data) {
    clearInterval(timer);
    lastResult = data;
    els.finalEmpty.hidden = true;
    els.finalAnswer.innerHTML = renderMarkdown(data.answer);
    if (data.draft) els.draftAnswer.innerHTML = renderMarkdown(data.draft);
    renderTrace(data.trace);
    setRoute(data.route);
    els.totalTime.textContent = `Total ${formatMs(data.total_ms)}`;
    showTab("final");
    setStatus(data.blocked ? "error" : "done", data.blocked ? "Blocked" : "Completed");
    addHistory({
      question: els.question.value.trim(),
      route: data.route,
      answer: data.answer,
      draft: data.draft,
      trace: data.trace,
      total_ms: data.total_ms,
      at: Date.now(),
    });
  }

  function fail(message) {
    clearInterval(timer);
    $$(".node.active").forEach((n) => {
      n.classList.remove("active");
      n.classList.add("blocked");
    });
    setProgress(1, true);
    setStatus("error", "Error");
    els.finalEmpty.hidden = true;
    els.finalAnswer.innerHTML = `<p class="muted">Something went wrong: ${message.replace(/[<>&]/g, "")}</p>`;
    toast(message, true);
  }

  /* ---------- run ---------- */
  function run(question) {
    if (source) source.close();

    resetPipeline();
    resetResult();
    showSkeleton();
    showTab("final");
    setBusy(true);
    setStatus("running", "Running");
    activate("guardrail");

    source = new EventSource(`/api/ask/stream?question=${encodeURIComponent(question)}`);

    source.addEventListener("step", (e) => handleStep(JSON.parse(e.data)));

    source.addEventListener("done", (e) => {
      handleDone(JSON.parse(e.data));
      source.close();
      setBusy(false);
    });

    source.addEventListener("failure", (e) => {
      fail(JSON.parse(e.data).message || "The pipeline failed.");
      source.close();
      setBusy(false);
    });

    source.onerror = () => {
      if (source.readyState === EventSource.CLOSED) return;
      source.close();
      fail("Lost connection to the server.");
      setBusy(false);
    };
  }

  els.form.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = els.question.value.trim();
    if (!q) {
      toast("Please type a question first.", true);
      els.question.focus();
      return;
    }
    run(q);
  });

  els.question.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      els.form.requestSubmit();
    }
  });

  els.question.addEventListener("input", () => {
    els.charCount.textContent = `${els.question.value.length} / 2000`;
  });

  $$(".chip[data-q]").forEach((chip) =>
    chip.addEventListener("click", () => {
      els.question.value = chip.dataset.q;
      els.question.dispatchEvent(new Event("input"));
      els.question.focus();
    })
  );

  els.reset.addEventListener("click", () => {
    if (source) source.close();
    clearInterval(timer);
    setBusy(false);
    els.question.value = "";
    els.question.dispatchEvent(new Event("input"));
    resetPipeline();
    resetResult();
    setStatus("", "Idle");
    els.question.focus();
  });

  els.copy.addEventListener("click", async () => {
    if (!lastResult?.answer) return toast("Nothing to copy yet.");
    try {
      await navigator.clipboard.writeText(lastResult.answer);
      toast("Answer copied to clipboard");
    } catch {
      toast("Could not copy.", true);
    }
  });

  /* ---------- history ---------- */
  function renderHistory() {
    const items = store.get(HISTORY_KEY, []);
    if (!items.length) {
      els.history.innerHTML = '<li class="h-empty">Your recent runs will appear here.</li>';
      return;
    }
    els.history.innerHTML = "";
    items.forEach((item, i) => {
      const li = document.createElement("li");
      li.innerHTML = `
        <div class="h-q"></div>
        <div class="h-meta">
          <span class="route-badge ${item.route}">${item.route}</span>
          <span>${formatMs(item.total_ms)} · ${new Date(item.at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
        </div>`;
      $(".h-q", li).textContent = item.question;
      li.addEventListener("click", () => restore(items[i]));
      els.history.appendChild(li);
    });
  }

  function addHistory(entry) {
    const items = store.get(HISTORY_KEY, []);
    items.unshift(entry);
    store.set(HISTORY_KEY, items.slice(0, 12));
    renderHistory();
  }

  function restore(item) {
    if (source) source.close();
    setBusy(false);
    resetPipeline();
    els.question.value = item.question;
    els.question.dispatchEvent(new Event("input"));
    lastResult = item;
    els.finalEmpty.hidden = true;
    els.finalAnswer.innerHTML = renderMarkdown(item.answer);
    els.draftAnswer.innerHTML = item.draft ? renderMarkdown(item.draft) : '<p class="muted">No draft.</p>';
    renderTrace(item.trace || []);
    setRoute(item.route);
    setStatus("done", "Restored");
    showTab("final");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  els.clearHistory.addEventListener("click", () => {
    store.set(HISTORY_KEY, []);
    renderHistory();
    toast("History cleared");
  });

  renderHistory();
})();
