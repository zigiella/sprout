/* Sprout landing-demo · try/rhizome — primera versión funcional */

(function () {
  const PRESETS = {
    dry: { soil_pct: 12, tank_pct: 70, heartbeat_age_s: 5 },
    ok: { soil_pct: 60, tank_pct: 65, heartbeat_age_s: 8 },
    tank_low: { soil_pct: 22, tank_pct: 14, heartbeat_age_s: 7 },
    heartbeat_lost: { soil_pct: 28, tank_pct: 60, heartbeat_age_s: 45 },
    modulated: { soil_pct: 8, tank_pct: 55, heartbeat_age_s: 6 }
  };

  const $ = id => document.getElementById(id);

  function applyPreset(name) {
    const p = PRESETS[name];
    if (!p) return;
    $("soil_pct").value = p.soil_pct;
    $("tank_pct").value = p.tank_pct;
    $("heartbeat_age_s").value = p.heartbeat_age_s;
  }

  $("preset").addEventListener("change", e => {
    if (e.target.value) applyPreset(e.target.value);
  });

  $("rhizome-form").addEventListener("submit", async ev => {
    ev.preventDefault();
    const state = {
      soil_pct: $("soil_pct").value,
      tank_pct: $("tank_pct").value,
      heartbeat_age_s: $("heartbeat_age_s").value
    };

    const receipt = $("receipt-output");
    const status = $("receipt-status");
    status.className = "status-pill warn";
    status.textContent = "deciding...";
    receipt.textContent = "Calling Rhizome (Gemma 4 E2B)...";
    $("rationale-es").textContent = "";
    $("rationale-en").textContent = "";

    try {
      const r = await window.SproutAPI.rhizomeDecide(state);
      receipt.textContent = JSON.stringify({
        decision_id: r.decision_id,
        action: r.action,
        reason: r.reason,
        candidate_action: r.candidate_action,
        final_action: r.final_action,
        modulated: r.modulated,
        issued_at: r.issued_at,
        valid_until_minutes: r.valid_until_minutes
      }, null, 2);

      $("rationale-es").textContent = r.rationale_es;
      $("rationale-en").textContent = r.rationale_en;

      if (r.action === "block") { status.className = "status-pill alert"; status.textContent = "BLOCK"; }
      else if (r.action === "skip") { status.className = "status-pill warn"; status.textContent = "SKIP"; }
      else if (r.modulated) { status.className = "status-pill warn"; status.textContent = "ESP32 SAFE_LIMIT"; }
      else { status.className = "status-pill ok"; status.textContent = "IRRIGATE"; }
    } catch (err) {
      status.className = "status-pill alert";
      status.textContent = "error";
      receipt.textContent = String(err);
    }
  });

  // ----------------- Live log -----------------

  const log = $("log-area");
  let logTimer = null;
  let entries = [];

  function logEntry(html) {
    entries.push(html);
    if (entries.length > 10) entries.shift();
    log.innerHTML = entries.join("\n");
    log.scrollTop = log.scrollHeight;
  }

  function ts() {
    const d = new Date();
    return d.toLocaleTimeString("en-GB");
  }

  async function tick() {
    // genera estado pseudo-aleatorio
    const state = {
      soil_pct: Math.floor(8 + Math.random() * 60),
      tank_pct: Math.floor(15 + Math.random() * 75),
      heartbeat_age_s: Math.random() < 0.05 ? 50 : Math.floor(Math.random() * 15)
    };
    try {
      const r = await window.SproutAPI.rhizomeDecide(state);
      let cls, label;
      if (r.action === "block") { cls = "ev-veto"; label = "VETO"; }
      else if (r.modulated) { cls = "ev-veto"; label = "MODULATED"; }
      else { cls = "ev-decision"; label = r.action.toUpperCase(); }

      const line = `<span class="ts">[${ts()}]</span> <span class="${cls}">${label}</span> ` +
        `soil=${state.soil_pct}% tank=${state.tank_pct}% ` +
        `→ ${r.action} (${r.final_action.seconds}s) · ${r.reason}`;
      logEntry(line);
    } catch (e) {
      logEntry(`<span class="ts">[${ts()}]</span> <span class="ev-veto">ERROR</span> ${e}`);
    }
  }

  $("log-toggle").addEventListener("click", () => {
    if (logTimer) {
      clearInterval(logTimer);
      logTimer = null;
      $("log-toggle").textContent = "Start log";
    } else {
      tick();
      logTimer = setInterval(tick, 2200);
      $("log-toggle").textContent = "Stop log";
    }
  });

  $("log-clear").addEventListener("click", () => {
    entries = [];
    log.innerHTML = "";
  });

})();
