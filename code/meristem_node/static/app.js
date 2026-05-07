// Meristem-nodo UI — vanilla JS, sin frameworks.
//
// Polling cada 2 segundos a /health, /status, /sync-state, /bundles/recent,
// /policies/recent. Si Pollen está conectado, los botones quedan
// habilitados; click dispara POST /pollen/command con el comando
// correspondiente.
//
// i18n: usa window.Meristem.i18n.t(key, params) para todos los strings
// visibles. Toggle ES/EN en topbar persiste preferencia en localStorage.
// Default ES.
//
// Diseñado para que Venation reescriba CSS sin tocar la lógica de fetch/state.

(function () {
  "use strict";

  const POLL_INTERVAL_MS = 2000;
  const I18N = (window.Meristem && window.Meristem.i18n)
    ? window.Meristem.i18n
    : { t: (k) => k, getLocale: () => "es", setLocale: () => {} };
  const t = I18N.t;

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
  const $bundlesTbody = document.getElementById("bundles-tbody");
  const $policiesTbody = document.getElementById("policies-tbody");
  const $bundlesMeta = document.getElementById("bundles-meta");
  const $policiesMeta = document.getElementById("policies-meta");
  const $langToggle = document.getElementById("lang-toggle");
  const $langOptES = document.getElementById("lang-es");
  const $langOptEN = document.getElementById("lang-en");

  // ----- State -----
  let state = {
    health: null,
    status: null,
    syncState: null,
    bundlesRecent: null,
    policiesRecent: null,
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
    if (!health) {
      $chipLLM.textContent = t("topbar.llm_loading");
      return;
    }

    const llmReal = health.llm_mode === "real";
    $chipLLM.textContent = llmReal ? t("topbar.llm_real") : t("topbar.llm_stub");
    $chipLLM.classList.toggle("active", llmReal);

    const pollenConn = (health.pollen_connection || syncState?.pollen_connection || {});
    if (pollenConn.connected) {
      const pid = pollenConn.pollen_id || "—";
      $chipPollen.textContent = t("topbar.pollen_connected", { id: pid });
      $chipPollen.classList.add("connected");
    } else {
      $chipPollen.textContent = t("topbar.pollen_disconnected");
      $chipPollen.classList.remove("connected");
    }
  }

  function renderStaticTexts() {
    // Texto fijo del DOM que solo cambia al cambiar idioma.
    document.querySelector(".logo-text").textContent = t("topbar.brand");
    document.title = t("topbar.brand");
    document.querySelector(".zone-dashboard .zone-title").textContent = t("zone1.title");
    document.querySelector(".zone-control .zone-title").textContent = t("zone2.title");
    document.querySelector(".zone-log .zone-title").textContent = t("zone3.title");
    document.querySelector(".zone-bundles .zone-title").textContent = t("zone4.title");
    document.querySelector(".zone-policies .zone-title").textContent = t("zone5.title");
    document.querySelector(".trazabilidad-label").textContent = t("zone1.trazabilidad_label");
    if ($emptyState) $emptyState.textContent = t("zone1.empty");
    $btnRecoger.textContent = t("zone2.btn_recoger");
    $btnCargar.textContent = t("zone2.btn_cargar");
    // Headers de tabla
    document.querySelectorAll("#bundles-table .col-time").forEach(el => { if (el.tagName === "TH") el.textContent = t("zone4.col_time"); });
    document.querySelectorAll("#bundles-table .col-target").forEach(el => { if (el.tagName === "TH") el.textContent = t("zone4.col_target"); });
    document.querySelectorAll("#bundles-table .col-pollen").forEach(el => { if (el.tagName === "TH") el.textContent = t("zone4.col_pollen"); });
    document.querySelectorAll("#bundles-table .col-reason").forEach(el => { if (el.tagName === "TH") el.textContent = t("zone4.col_reason"); });
    document.querySelectorAll("#policies-table .col-time").forEach(el => { if (el.tagName === "TH") el.textContent = t("zone5.col_time"); });
    document.querySelectorAll("#policies-table .col-target").forEach(el => { if (el.tagName === "TH") el.textContent = t("zone5.col_target"); });
    document.querySelectorAll("#policies-table .col-mode").forEach(el => { if (el.tagName === "TH") el.textContent = t("zone5.col_mode"); });
    document.querySelectorAll("#policies-table .col-validity").forEach(el => { if (el.tagName === "TH") el.textContent = t("zone5.col_validity"); });
    document.querySelectorAll("#policies-table .col-rationale").forEach(el => { if (el.tagName === "TH") el.textContent = t("zone5.col_rationale"); });
    // Active locale toggle
    $langOptES.classList.toggle("active", I18N.getLocale() === "es");
    $langOptEN.classList.toggle("active", I18N.getLocale() === "en");
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

    status.targets.forEach(target => {
      seen.add(target.target_node_id);
      let card = existing.get(target.target_node_id);
      if (!card) {
        card = createCard(target);
        $cardsGrid.appendChild(card);
      }
      updateCard(card, target);
    });

    // Eliminar cards que ya no están
    existing.forEach((card, key) => {
      if (!seen.has(key)) card.remove();
    });

    // Última sync (más reciente entre last_bundle_at)
    const mostRecent = status.targets
      .map(target => target.last_bundle_at)
      .filter(Boolean)
      .sort()
      .pop();
    if (mostRecent) {
      $lastSync.textContent = t("zone1.last_sync", { when: formatRelative(mostRecent) });
    }
  }

  function createCard(target) {
    const card = document.createElement("article");
    card.className = "card";
    card.dataset.target = target.target_node_id;
    card.innerHTML = `
      <div class="card-header">
        <span class="card-title">${escape(target.target_node_id)}</span>
        <span class="card-mode-tag" data-mode="unknown">${escape(t("zone1.card.no_mode"))}</span>
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
      ? t("zone1.card.no_mode")
      : mode.toUpperCase();

    // Reason info via i18n keys "rc.<reason_code>.tag" + "rc.<reason_code>.text"
    const rc = target.latest_reason_code || "null";
    const tagKey = `rc.${rc}.tag`;
    const textKey = `rc.${rc}.text`;
    const tagStr = t(tagKey);
    const textStr = t(textKey);
    // Si la key no existe, t() devuelve la key — fallback al raw reason_code
    card.querySelector(".card-reason").textContent =
      tagStr === tagKey ? (target.latest_reason_code || "—") : tagStr;
    card.querySelector(".card-rationale").textContent =
      textStr === textKey ? (target.latest_reason_code || t("rc.null.text")) : textStr;

    const meta = card.querySelector(".card-meta");
    const refused = target.bundles_received - target.policies_emitted;
    const validityStr = target.latest_policy_valid_until
      ? t("zone5.validity_prefix") + formatDate(target.latest_policy_valid_until)
      : "";
    meta.innerHTML = `
      <span class="card-meta-bundles">${target.bundles_received} bundles</span>
      <span class="card-meta-policies">${target.policies_emitted} policies</span>
      ${refused > 0 ? `<span class="card-meta-badge">${refused} rechazo${refused > 1 ? "s" : ""}</span>` : ""}
      <span class="card-meta-validity">${escape(validityStr)}</span>
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
      const since = pollenConn.connected_at ? formatRelative(pollenConn.connected_at) : t("time.dash");
      $pollenStatus.textContent = t("zone2.status_connected", { id: pid, when: since });
      $pollenStatus.classList.add("connected");
      $btnRecoger.disabled = state.activeOperation !== null;
      $btnCargar.disabled = state.activeOperation !== null;
      $pollenMeta.textContent = t("zone2.meta_online");
    } else {
      $pollenStatus.textContent = t("zone2.status_disconnected");
      $pollenStatus.classList.remove("connected");
      $btnRecoger.disabled = true;
      $btnCargar.disabled = true;
      $pollenMeta.textContent = t("zone2.meta_offline");
    }
  }

  function renderEventLog(syncState) {
    if (!syncState || !syncState.recent_events || syncState.recent_events.length === 0) {
      $eventLog.innerHTML = `<li class="event-empty">${escape(t("zone3.empty"))}</li>`;
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

  function renderBundlesRecent(bundlesData) {
    if (!bundlesData || !bundlesData.items || bundlesData.items.length === 0) {
      $bundlesTbody.innerHTML = `<tr class="trail-empty"><td colspan="4">${escape(t("zone4.empty"))}</td></tr>`;
      $bundlesMeta.textContent = "0";
      return;
    }
    const items = bundlesData.items.slice(0, 12);
    $bundlesMeta.textContent = t("zone4.meta_count", { shown: items.length, total: bundlesData.items.length });
    $bundlesTbody.innerHTML = items.map(b => {
      const time = formatTime(b.received_at);
      const rc = b.reason_code || "null";
      const tagKey = `rc.${rc}.tag`;
      const tagStr = t(tagKey);
      const reason = (tagStr === tagKey ? (b.reason_code || "—") : tagStr);
      const ruleClass = b.rule_applied || "";
      return `<tr>
        <td class="col-time">${time}</td>
        <td class="col-target mono">${escape(b.target_rhizome_id || "—")}</td>
        <td class="col-pollen mono">${escape(b.source_pollen_id || "—")}</td>
        <td class="col-reason">
          <span class="reason-chip" data-rule="${escape(ruleClass)}">${escape(reason)}</span>
        </td>
      </tr>`;
    }).join("");
  }

  function renderPoliciesRecent(policiesData) {
    if (!policiesData || !policiesData.items || policiesData.items.length === 0) {
      $policiesTbody.innerHTML = `<tr class="trail-empty"><td colspan="5">${escape(t("zone5.empty"))}</td></tr>`;
      $policiesMeta.textContent = "0";
      return;
    }
    const items = policiesData.items.slice(0, 12);
    $policiesMeta.textContent = t("zone5.meta_count", { shown: items.length, total: policiesData.items.length });
    $policiesTbody.innerHTML = items.map(p => {
      const time = formatTime(p.emitted_at);
      const mode = p.mode_default || "unknown";
      const validity = p.valid_until ? formatDate(p.valid_until) : t("time.dash");
      // policy_id mostrado abreviado: pkt_meristem_xxxxx_yyyyy → pkt_..._yyyyy
      const policyShort = p.policy_id
        ? p.policy_id.length > 24
          ? p.policy_id.slice(0, 12) + "…" + p.policy_id.slice(-8)
          : p.policy_id
        : "—";
      const modeLabel = mode === "unknown" ? t("zone1.card.no_mode") : mode.toUpperCase();
      return `<tr>
        <td class="col-time">${time}</td>
        <td class="col-target mono" title="${escape(p.policy_id || "")}">
          ${escape(p.target_node_id || "—")}<br>
          <span class="policy-id-short">${escape(policyShort)}</span>
        </td>
        <td class="col-mode">
          <span class="mode-inline" data-mode="${escape(mode)}">${escape(modeLabel)}</span>
        </td>
        <td class="col-validity">${escape(validity)}</td>
        <td class="col-rationale" title="${escape(p.rationale_short || "")}">${escape(p.rationale_short || "—")}</td>
      </tr>`;
    }).join("");
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

  function _localeForIntl() {
    return I18N.getLocale() === "en" ? "en-GB" : "es-ES";
  }

  function formatTime(iso) {
    try {
      const d = new Date(iso);
      return d.toLocaleTimeString(_localeForIntl(), { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    } catch { return t("time.dash"); }
  }

  function formatDate(iso) {
    try {
      const d = new Date(iso);
      return d.toLocaleDateString(_localeForIntl(), { day: "2-digit", month: "short" });
    } catch { return t("time.dash"); }
  }

  function formatRelative(iso) {
    try {
      const then = new Date(iso).getTime();
      const now = Date.now();
      const diffSec = Math.floor((now - then) / 1000);
      if (diffSec < 60) return t("time.seconds_ago", { n: diffSec });
      if (diffSec < 3600) return t("time.minutes_ago", { n: Math.floor(diffSec / 60) });
      if (diffSec < 86400) return t("time.hours_ago", { n: Math.floor(diffSec / 3600) });
      return t("time.days_ago", { n: Math.floor(diffSec / 86400) });
    } catch { return t("time.dash"); }
  }

  // ----- Botones de comando -----

  async function triggerCommand(command, labelKey) {
    if (state.activeOperation) return;
    state.activeOperation = command;
    const label = t(labelKey);
    $progressLine.textContent = t("zone2.progress_in_progress", { label });
    $progressLine.classList.add("active");
    try {
      const result = await postCommand(command, 0);
      $progressLine.textContent = t("zone2.progress_sent", { label, trace: result.trace_id });
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
      $progressLine.textContent = t("zone2.progress_error", { msg: e.message });
      $progressLine.classList.remove("active");
      setTimeout(() => { $progressLine.textContent = ""; }, 4000);
    }
  }

  $btnRecoger.addEventListener("click", () => {
    triggerCommand("push_bundles", "zone2.label_recoger");
  });
  $btnCargar.addEventListener("click", () => {
    triggerCommand("pull_policies", "zone2.label_cargar");
  });

  // ----- Listener toggle ES/EN -----

  if ($langToggle) {
    $langToggle.addEventListener("click", (e) => {
      const opt = e.target.closest(".lang-opt");
      if (!opt || !opt.dataset.locale) return;
      I18N.setLocale(opt.dataset.locale);
    });
  }
  window.addEventListener("meristem:localechange", () => {
    renderStaticTexts();
    refresh();
  });

  // ----- Loop principal -----

  async function refresh() {
    const [health, status, syncState, bundlesRecent, policiesRecent] = await Promise.all([
      fetchJSON("/health"),
      fetchJSON("/status"),
      fetchJSON("/sync-state"),
      fetchJSON("/bundles/recent?limit=20"),
      fetchJSON("/policies/recent?limit=20"),
    ]);
    if (health) state.health = health;
    if (status) state.status = status;
    if (syncState) state.syncState = syncState;
    if (bundlesRecent) state.bundlesRecent = bundlesRecent;
    if (policiesRecent) state.policiesRecent = policiesRecent;

    renderTopbar(state.health, state.syncState);
    renderCards(state.status);
    renderTrazabilidad(state.health);
    renderControlPanel(state.health, state.syncState);
    renderEventLog(state.syncState);
    renderBundlesRecent(state.bundlesRecent);
    renderPoliciesRecent(state.policiesRecent);

    if (state.health) {
      $footerMeta.textContent = t("footer.text", {
        id: state.health.meristem_id || "—",
        version: state.health.version || "0.1",
      });
    }
  }

  // Arranque
  renderStaticTexts();
  refresh();
  setInterval(refresh, POLL_INTERVAL_MS);

})();
