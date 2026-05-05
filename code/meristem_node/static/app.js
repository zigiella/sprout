// Meristem-nodo UI v0 — vanilla JS, sin frameworks.
//
// Polling cada 2 segundos a /health, /status, /sync-state.
// Si Pollen está conectado, los botones quedan habilitados;
// click dispara POST /pollen/command con el comando correspondiente.
//
// Diseñado para que Venation reescriba el render con su sistema visual
// real (sprout_design_pack_v1) sin tocar la lógica de fetch/state.

(function () {
  "use strict";

  const POLL_INTERVAL_MS = 2000;
  const REASON_CODE_LABELS = {
    "STABLE_BUNDLE":            { tag: "ESTABLE",    text: "Tu Rhizome funciona con normalidad." },
    "EVIDENCE_LOW_CONFIDENCE":  { tag: "PRUDENCIA",  text: "Datos ambiguos en la última visita." },
    "PERSISTENT_EMERGENCY":     { tag: "ALERTA",     text: "Hay alerta persistente. Revisa." },
    "HARD_LIMIT_DOMAIN":        { tag: "LÍMITE",     text: "Límite del firmware ESP32." },
    "JURISDICTION_POLLEN":      { tag: "VIA POLLEN", text: "Cambio puntual: usa Pollen." },
  };

  // ----- DOM refs -----
  const $chipLLM = document.getElementById("chip-llm");
  const $chipPollen = document.getElementById("chip-pollen");
  const $cardsGrid = document.getElementById("cards-grid");
  const $emptyState = document.getElementById("empty-state");
  const $lastSync = document.getElementById("last-sync");
  const $pollenStatus = document.getElementById("pollen-status");
  const $pollenMeta = document.getElementById("pollen-meta");
  const $btnRecoger = document.getElementById("btn-recoger");
  const $btnCargar = document.getElementById("btn-cargar");
  const $progressLine = document.getElementById("progress-line");
  const $eventLog = document.getElementById("event-log");
  const $footerMeta = document.getElementById("footer-meta");
  const $trazabilidadPills = document.querySelectorAll(".pill[data-rule]");

  // ----- State -----
  let state = {
    health: null,
    status: null,
    syncState: null,
    activeOperation: null,  // "push_bundles" | "pull_policies" | null
  };

  // ----- Fetch helpers -----
  async function fetchJSON(url) {
    try {
      const r = await fetch(url, { cache: "no-store" });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json();
    } catch (e) {
      console.warn("fetch failed:", url, e);
      return null;
    }
  }

  async function postCommand(command, expectedCount) {
    const r = await fetch("/pollen/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command, expected_count: expectedCount || 0 }),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${r.status}`);
    }
    return await r.json();
  }

  // ----- Render -----

  function renderTopbar(health, syncState) {
    if (!health) return;

    const llmReal = health.llm_mode === "real";
    $chipLLM.textContent = llmReal ? "LLM: Real" : "LLM: Stub";
    $chipLLM.classList.toggle("active", llmReal);

    const pollenConn = (health.pollen_connection || syncState?.pollen_connection || {});
    if (pollenConn.connected) {
      const pid = pollenConn.pollen_id || "—";
      $chipPollen.textContent = `Pollen: ${pid}`;
      $chipPollen.classList.add("connected");
    } else {
      $chipPollen.textContent = "Pollen: desconectado";
      $chipPollen.classList.remove("connected");
    }
  }

  function renderCards(status) {
    if (!status || !status.targets || status.targets.length === 0) {
      $emptyState.style.display = "block";
      Array.from($cardsGrid.querySelectorAll(".card")).forEach(c => c.remove());
      return;
    }
    $emptyState.style.display = "none";

    const existing = new Map();
    Array.from($cardsGrid.querySelectorAll(".card")).forEach(c => {
      existing.set(c.dataset.target, c);
    });

    const seen = new Set();

    status.targets.forEach(t => {
      seen.add(t.target_node_id);
      let card = existing.get(t.target_node_id);
      if (!card) {
        card = createCard(t);
        $cardsGrid.appendChild(card);
      }
      updateCard(card, t);
    });

    // Eliminar cards que ya no están
    existing.forEach((card, key) => {
      if (!seen.has(key)) card.remove();
    });

    // Última sync (más reciente entre last_bundle_at)
    const mostRecent = status.targets
      .map(t => t.last_bundle_at)
      .filter(Boolean)
      .sort()
      .pop();
    if (mostRecent) {
      $lastSync.textContent = `Última sync: ${formatRelative(mostRecent)}`;
    }
  }

  function createCard(target) {
    const card = document.createElement("article");
    card.className = "card";
    card.dataset.target = target.target_node_id;
    card.innerHTML = `
      <div class="card-header">
        <span class="card-title">${escape(target.target_node_id)}</span>
        <span class="card-mode-tag" data-mode="unknown">—</span>
      </div>
      <div class="card-reason">—</div>
      <div class="card-rationale">—</div>
      <div class="card-meta">
        <span class="card-meta-bundles">0 bundles</span>
        <span class="card-meta-policies">0 policies</span>
        <span class="card-meta-validity">—</span>
      </div>
    `;
    return card;
  }

  function updateCard(card, target) {
    const mode = target.latest_policy_mode || "unknown";
    card.dataset.mode = mode;
    card.querySelector(".card-mode-tag").dataset.mode = mode;
    card.querySelector(".card-mode-tag").textContent = mode === "unknown"
      ? "—"
      : mode.toUpperCase();

    const reasonInfo = REASON_CODE_LABELS[target.latest_reason_code] || {
      tag: "—",
      text: target.latest_reason_code || "Sin policy todavía",
    };
    card.querySelector(".card-reason").textContent = reasonInfo.tag;
    card.querySelector(".card-rationale").textContent = reasonInfo.text;

    const meta = card.querySelector(".card-meta");
    const refused = target.bundles_received - target.policies_emitted;
    meta.innerHTML = `
      <span class="card-meta-bundles">${target.bundles_received} bundles</span>
      <span class="card-meta-policies">${target.policies_emitted} policies</span>
      ${refused > 0 ? `<span class="card-meta-badge">${refused} rechazo${refused > 1 ? "s" : ""}</span>` : ""}
      <span class="card-meta-validity">${target.latest_policy_valid_until ? "vál. " + formatDate(target.latest_policy_valid_until) : ""}</span>
    `;
  }

  function renderTrazabilidad(health) {
    if (!health || !health.decisions_by_rule) return;
    const counts = health.decisions_by_rule || {};
    $trazabilidadPills.forEach(pill => {
      const rule = pill.dataset.rule;
      const ruleShort = rule.replace("_policy", "");
      pill.textContent = `${ruleShort}: ${counts[rule] || 0}`;
    });
  }

  function renderControlPanel(health, syncState) {
    const pollenConn = (health?.pollen_connection || syncState?.pollen_connection || {});
    const isConnected = !!pollenConn.connected && !!pollenConn.alive;

    if (isConnected) {
      const pid = pollenConn.pollen_id || "—";
      const since = pollenConn.connected_at ? formatRelative(pollenConn.connected_at) : "—";
      $pollenStatus.textContent = `Pollen ${pid} conectado · ${since}`;
      $pollenStatus.classList.add("connected");
      $btnRecoger.disabled = state.activeOperation !== null;
      $btnCargar.disabled = state.activeOperation !== null;
      $pollenMeta.textContent = "online";
    } else {
      $pollenStatus.textContent = "Pollen no detectado";
      $pollenStatus.classList.remove("connected");
      $btnRecoger.disabled = true;
      $btnCargar.disabled = true;
      $pollenMeta.textContent = "offline";
    }
  }

  function renderEventLog(syncState) {
    if (!syncState || !syncState.recent_events || syncState.recent_events.length === 0) {
      $eventLog.innerHTML = '<li class="event-empty">Sin eventos todavía.</li>';
      return;
    }
    const items = syncState.recent_events.slice(0, 12).map(ev => {
      const time = formatTime(ev.created_at);
      const arrow = ev.direction === "in" ? "←" : "→";
      const arrowClass = ev.direction;
      const trace = ev.trace_id ? `<span class="event-trace">${escape(ev.trace_id)}</span>` : "";
      return `<li class="event-row">
        <span class="event-time">${time}</span>
        <span class="event-arrow ${arrowClass}">${arrow}</span>
        <span class="event-name">${escape(ev.event)}</span>
        ${trace}
      </li>`;
    });
    $eventLog.innerHTML = items.join("");
  }

  // ----- Helpers -----

  function escape(str) {
    if (str == null) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatTime(iso) {
    try {
      const d = new Date(iso);
      return d.toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    } catch { return "—"; }
  }

  function formatDate(iso) {
    try {
      const d = new Date(iso);
      return d.toLocaleDateString("es-ES", { day: "2-digit", month: "short" });
    } catch { return "—"; }
  }

  function formatRelative(iso) {
    try {
      const then = new Date(iso).getTime();
      const now = Date.now();
      const diffSec = Math.floor((now - then) / 1000);
      if (diffSec < 60) return `hace ${diffSec}s`;
      if (diffSec < 3600) return `hace ${Math.floor(diffSec / 60)}m`;
      if (diffSec < 86400) return `hace ${Math.floor(diffSec / 3600)}h`;
      return `hace ${Math.floor(diffSec / 86400)}d`;
    } catch { return "—"; }
  }

  // ----- Botones de comando -----

  async function triggerCommand(command, label) {
    if (state.activeOperation) return;
    state.activeOperation = command;
    $progressLine.textContent = `${label} en curso…`;
    $progressLine.classList.add("active");
    try {
      const result = await postCommand(command, 0);
      $progressLine.textContent = `${label} enviado · trace ${result.trace_id}`;
      // Tras 5s liberamos el lock; en producción esperaríamos
      // bundles_pushed/policies_pulled del cliente WS.
      setTimeout(() => {
        state.activeOperation = null;
        $progressLine.textContent = "";
        $progressLine.classList.remove("active");
        refresh();
      }, 5000);
    } catch (e) {
      state.activeOperation = null;
      $progressLine.textContent = `Error: ${e.message}`;
      $progressLine.classList.remove("active");
      setTimeout(() => { $progressLine.textContent = ""; }, 4000);
    }
  }

  $btnRecoger.addEventListener("click", () => {
    triggerCommand("push_bundles", "Recoger visitas");
  });
  $btnCargar.addEventListener("click", () => {
    triggerCommand("pull_policies", "Cargar policies");
  });

  // ----- Loop principal -----

  async function refresh() {
    const [health, status, syncState] = await Promise.all([
      fetchJSON("/health"),
      fetchJSON("/status"),
      fetchJSON("/sync-state"),
    ]);
    if (health) state.health = health;
    if (status) state.status = status;
    if (syncState) state.syncState = syncState;

    renderTopbar(state.health, state.syncState);
    renderCards(state.status);
    renderTrazabilidad(state.health);
    renderControlPanel(state.health, state.syncState);
    renderEventLog(state.syncState);

    if (state.health) {
      $footerMeta.textContent = `Meristem ${state.health.meristem_id || "—"} v${state.health.version || "0.1"} · slow brain doméstico`;
    }
  }

  // Arranque
  refresh();
  setInterval(refresh, POLL_INTERVAL_MS);

})();
