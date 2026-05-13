/*
  Sprout landing-demo · cliente API Gemma 4
  ------------------------------------------------------------
  Feature-flag SPROUT_API_MODE controla si la demo llama a una API
  real de Gemma 4 (Modal / HF Inference / Cloud Run) o si usa un
  generador mock determinista para testar sin dependencias.

  Patrón conservador: por defecto MOCK. Cuando Bea + Cambium
  configuren los endpoints reales, cambiamos SPROUT_API_MODE a
  "live" y rellenamos las URLs de SPROUT_API_ENDPOINTS abajo.

  Diseño: el mock devuelve respuestas plausibles para los 3 casos
  (Rhizome E2B, Pollen E4B, Meristem E4B) lo bastante reales para
  que el jurado vea cómo funciona la cadena. Cuando llegue la API
  real, el output será de Gemma 4 vivo, no de este mock.
*/

const SPROUT_API_MODE = "mock"; // "mock" | "live"

// Optional live mode — point each node at a hosted Gemma 4 inference endpoint
// (e.g. Modal, HF Inference). The browser demo runs deterministic by design;
// this hook is only for users who want to wire their own backend.
const SPROUT_API_ENDPOINTS = {
  rhizome_e2b: null, // e.g. "https://your-host/gemma-4-e2b"
  pollen_e4b: null,  // e.g. "https://your-host/gemma-4-e4b-audio"
  meristem_e4b: null // e.g. "https://your-host/gemma-4-e4b-tools"
};

// ----------------------------------------------------------------
// Live mode (only active when SPROUT_API_MODE === "live")
// ----------------------------------------------------------------

async function callGemmaLive(endpoint, payload) {
  if (!endpoint) {
    throw new Error("SPROUT_API_ENDPOINTS not configured. Set SPROUT_API_MODE='mock' or fill endpoints.");
  }
  const resp = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!resp.ok) {
    const err = await resp.text().catch(() => "(no body)");
    throw new Error(`API ${resp.status}: ${err}`);
  }
  return resp.json();
}

// ----------------------------------------------------------------
// Mock determinista para los 3 casos (Rhizome / Pollen / Meristem)
// ----------------------------------------------------------------

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

async function rhizomeDecideMock(state) {
  // simulamos latencia de inferencia local Jetson
  await delay(900 + Math.random() * 600);
  const soil = Number(state.soil_pct ?? 28);
  const tank = Number(state.tank_pct ?? 65);
  const heartbeat_age = Number(state.heartbeat_age_s ?? 8);

  let action, reason, candidate_seconds = 18;
  if (heartbeat_age > 30) {
    action = "block";
    reason = "JETSON_HEARTBEAT_LOST";
    candidate_seconds = 0;
  } else if (tank < 20) {
    action = "block";
    reason = "TANK_LOW";
    candidate_seconds = 0;
  } else if (soil > 55) {
    action = "skip";
    reason = "SOIL_OK_ENOUGH";
    candidate_seconds = 0;
  } else if (soil < 15) {
    action = "irrigate";
    reason = "SOIL_DRY_THRESHOLD_REACHED";
    candidate_seconds = 26;
  } else {
    action = "irrigate";
    reason = "SOIL_BELOW_OPTIMUM";
    candidate_seconds = 18;
  }

  // ESP32 hard limit del firmware MVP: MAX_WATER_SECONDS_MVP = 30. Si la
  // candidate excede 30, el firmware REAL responde REJECT con motivo
  // EVENT_DURATION_OUT_OF_RANGE (no modula). Este mock determinista refleja
  // esa semantica: si esta sobre el limite, queda fuera de envelope.
  // La "modulacion" que aparecia antes (Math.min) no estaba en el firmware
  // contractual y se rebajo tras la auditoria dia 28.
  const FIRMWARE_MAX_SECONDS = 30;
  const final_seconds = candidate_seconds <= FIRMWARE_MAX_SECONDS ? candidate_seconds : 0;
  const modulated = false;
  if (final_seconds === 0 && action === "irrigate") {
    action = "block";
    reason = "EVENT_DURATION_OUT_OF_RANGE";
  }

  return {
    decision_id: "dec_" + Date.now().toString(36),
    action,
    reason,
    candidate_action: { kind: action, seconds: candidate_seconds },
    final_action: { kind: action, seconds: final_seconds },
    modulated,
    rationale_es: rationaleRhizome(action, reason, soil, tank, modulated, candidate_seconds, final_seconds),
    rationale_en: rationaleRhizomeEn(action, reason, soil, tank, modulated, candidate_seconds, final_seconds),
    issued_at: new Date().toISOString(),
    valid_until_minutes: 30
  };
}

function rationaleRhizome(action, reason, soil, tank, modulated, cand, final_s) {
  if (action === "block" && reason === "TANK_LOW") {
    return `Bloqueo el riego: el depósito está al ${tank}%, por debajo del mínimo del firmware.`;
  }
  if (action === "block" && reason === "JETSON_HEARTBEAT_LOST") {
    return `Bloqueo el riego: Jetson sin heartbeat por más de 30s. El sistema baja a estado seguro.`;
  }
  if (action === "skip") {
    return `Salto el evento: humedad ${soil}% ya está cómoda, no necesita agua ahora.`;
  }
  if (modulated) {
    return `Riego ${final_s}s. Pedí ${cand}s pero el ESP32 los recortó al sobre seguro (max ${final_s}s por evento).`;
  }
  return `Riego ${final_s}s. Humedad ${soil}%, depósito ${tank}%, dentro del envelope seguro.`;
}

function rationaleRhizomeEn(action, reason, soil, tank, modulated, cand, final_s) {
  if (action === "block" && reason === "TANK_LOW") {
    return `Blocked irrigation: tank at ${tank}%, below firmware minimum.`;
  }
  if (action === "block" && reason === "JETSON_HEARTBEAT_LOST") {
    return `Blocked irrigation: Jetson heartbeat lost over 30s. System falls back to safe state.`;
  }
  if (action === "skip") {
    return `Skipping event: soil at ${soil}% is comfortable, no water needed now.`;
  }
  if (modulated) {
    return `Watering ${final_s}s. Requested ${cand}s but ESP32 SAFE_LIMIT capped to ${final_s}s.`;
  }
  return `Watering ${final_s}s. Soil ${soil}%, tank ${tank}%, within safe envelope.`;
}

async function pollenCompileMock(transcript) {
  await delay(1100 + Math.random() * 700); // simula inferencia E4B audio multimodal
  const t = (transcript || "").toLowerCase();

  // heuristicas mock — el real LLM hace mejor
  let priority_plot = "A";
  if (t.includes("parcela b") || t.includes("plot b")) priority_plot = "B";

  let horizon_h = 72;
  const m = t.match(/(\d+)\s*(h(oras)?|hour)/);
  if (m) horizon_h = Number(m[1]);

  let dry_threshold = 35;
  if (t.includes("seca") || t.includes("menos") || t.includes("drier") || t.includes("less"))
    dry_threshold = 25;

  let budget_cap_ml = 1500;
  if (t.includes("menos") || t.includes("less")) budget_cap_ml = 900;

  // simula "confianza suficiente" (4 checks de Mini-Evaluator)
  const tooShort = t.length < 6;
  const noKeyword = !(t.match(/(rieg|wat|pollen|less|menos|seca|deposit|tank|parcel|plot)/i));
  const confidence_ok = !tooShort && !noKeyword;

  if (!confidence_ok) {
    return {
      action: "REFUSE_RETRY",
      reason: "LLM_LOW_CONFIDENCE",
      message_es: "No estoy seguro de cómo aplicar esto. ¿Puedes repetirlo o decirlo de otra forma?",
      message_en: "I'm not sure how to apply this. Can you repeat or rephrase?",
      transcript
    };
  }

  return {
    action: "APPLY_AS_IS",
    reason: "STABLE_INTENT",
    mission_patch: {
      target_node_id: priority_plot === "A" ? "rhizome_01" : "rhizome_02",
      priority_plot,
      horizon_h,
      soil_thresholds: { dry: dry_threshold },
      budget_cap_ml,
      operator_note: transcript || ""
    },
    rationale_es: `Compilé tu instrucción: prioridad parcela ${priority_plot}, próximas ${horizon_h}h, riego más conservador (umbral seco ${dry_threshold}%, tope ${budget_cap_ml}ml).`,
    rationale_en: `Compiled your instruction: plot ${priority_plot} priority, next ${horizon_h}h, more conservative irrigation (dry threshold ${dry_threshold}%, cap ${budget_cap_ml}ml).`,
    valid_until_h: 12
  };
}

async function meristemEvaluateMock(bundle) {
  await delay(1400 + Math.random() * 600); // simula tool calling chain
  const decisions = bundle?.recent_decisions || [];
  const blocks = decisions.filter(d => d.action === "block").length;
  const conf = bundle?.avg_confidence ?? 0.85;

  let mode = "stable";
  let rationale_es = "Confirmo política activa: bundle limpio, alta confianza, sin alertas persistentes.";
  let rationale_en = "Confirming active policy: clean bundle, high confidence, no persistent alerts.";

  if (blocks >= 2) {
    mode = "alert";
    rationale_es = `Política en modo alerta: ${blocks} bloqueos consecutivos detectados, no es ruido.`;
    rationale_en = `Policy in alert mode: ${blocks} consecutive blocks detected — not noise.`;
  } else if (conf < 0.7) {
    mode = "conservative";
    rationale_es = "Política conservadora: confianza media baja en los receipts del bundle.";
    rationale_en = "Conservative policy: average confidence in bundle receipts is low.";
  }

  return {
    policy_id: "pol_" + Date.now().toString(36),
    mode_default: mode,
    soil_thresholds: { dry: mode === "conservative" ? 35 : 30 },
    daily_budget_ml: mode === "alert" ? 600 : 1500,
    valid_until_days: 7,
    rationale_es,
    rationale_en,
    decisions_by_rule: {
      stable: blocks === 0 ? 1 : 0,
      alert: blocks >= 2 ? 1 : 0,
      conservative: (blocks < 2 && conf < 0.7) ? 1 : 0,
      refuse: 0
    }
  };
}

// ----------------------------------------------------------------
// API pública usada por las páginas /try
// ----------------------------------------------------------------

window.SproutAPI = {
  mode: SPROUT_API_MODE,

  async rhizomeDecide(state) {
    if (SPROUT_API_MODE === "mock") return rhizomeDecideMock(state);
    return callGemmaLive(SPROUT_API_ENDPOINTS.rhizome_e2b, { type: "rhizome.decide", state });
  },

  async pollenCompile(transcript) {
    if (SPROUT_API_MODE === "mock") return pollenCompileMock(transcript);
    return callGemmaLive(SPROUT_API_ENDPOINTS.pollen_e4b, { type: "pollen.compile", transcript });
  },

  async meristemEvaluate(bundle) {
    if (SPROUT_API_MODE === "mock") return meristemEvaluateMock(bundle);
    return callGemmaLive(SPROUT_API_ENDPOINTS.meristem_e4b, { type: "meristem.evaluate", bundle });
  }
};
