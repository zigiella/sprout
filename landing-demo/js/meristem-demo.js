/* Sprout landing-demo · try/meristem — primera versión funcional */

(function () {
  const $ = id => document.getElementById(id);

  const SCENARIOS = {
    stable: {
      r01: `scenario: stable
last 7 days:
  decisions: 28 irrigate, 4 skip, 0 block
  avg confidence: 0.91
  alerts persistent: 0
weather_digest: ok`,
      r02: `scenario: stable
last 7 days:
  decisions: 24 irrigate, 6 skip, 1 block
  avg confidence: 0.88
  alerts persistent: 0
weather_digest: from_rhizome_01 (ferry by Pollen)`,
      bundle: { recent_decisions: [{action:"block"}], avg_confidence: 0.90 }
    },
    alert: {
      r01: `scenario: alert
last 7 days:
  decisions: 22 irrigate, 2 skip, 4 block (TANK_LOW)
  avg confidence: 0.85
  alerts persistent: 2
weather_digest: ok`,
      r02: `scenario: stable
last 7 days:
  decisions: 26 irrigate, 5 skip, 1 block
  avg confidence: 0.86
  alerts persistent: 0
weather_digest: from_rhizome_01`,
      bundle: { recent_decisions: [{action:"block"},{action:"block"},{action:"block"}], avg_confidence: 0.85 }
    },
    conservative: {
      r01: `scenario: mixed
last 7 days:
  decisions: 25 irrigate, 4 skip, 1 block
  avg confidence: 0.62
  validation_stamps: 3 disputed
weather_digest: contradictory readings`,
      r02: `scenario: mixed
last 7 days:
  decisions: 22 irrigate, 5 skip, 0 block
  avg confidence: 0.65
  validation_stamps: 2 caution
weather_digest: from_rhizome_01 (some receipts disputed)`,
      bundle: { recent_decisions: [{action:"block"}], avg_confidence: 0.63 }
    }
  };

  function applyScenario(name) {
    const s = SCENARIOS[name];
    if (!s) return;
    $("r01").textContent = s.r01;
    $("r02").textContent = s.r02;
  }

  $("scenario").addEventListener("change", e => applyScenario(e.target.value));

  $("meristem-form").addEventListener("submit", async ev => {
    ev.preventDefault();
    const sName = $("scenario").value;
    const s = SCENARIOS[sName];
    if (!s) return;

    const pipe = $("meristem-pipeline");
    const out = $("policy-output");
    const rules = $("rules-output");

    out.textContent = "...";
    rules.textContent = "evaluating...";
    $("meristem-rationale-es").textContent = "";
    $("meristem-rationale-en").textContent = "";

    pipe.innerHTML = `<span class="status-pill warn">evaluating</span> Gemma 4 E4B + tool calling...`;

    try {
      const r = await window.SproutAPI.meristemEvaluate(s.bundle);

      pipe.innerHTML = `<span class="status-pill ok">${r.mode_default.toUpperCase()}</span> policy emitted, valid for ${r.valid_until_days} days`;

      out.textContent = JSON.stringify({
        policy_id: r.policy_id,
        mode_default: r.mode_default,
        soil_thresholds: r.soil_thresholds,
        daily_budget_ml: r.daily_budget_ml,
        valid_until_days: r.valid_until_days,
        policy_origin: "meristem-durable"
      }, null, 2);

      $("meristem-rationale-es").textContent = r.rationale_es;
      $("meristem-rationale-en").textContent = r.rationale_en;

      const dr = r.decisions_by_rule;
      rules.textContent =
        `stable:        ${dr.stable}
alert:         ${dr.alert}
conservative:  ${dr.conservative}
refuse:        ${dr.refuse}

(Sprout exposes this on /health — judges and farmers can see which rule
fires most often. Not debug metadata; visible accountability.)`;
    } catch (err) {
      pipe.innerHTML = `<span class="status-pill alert">ERROR</span> ${err}`;
      out.textContent = String(err);
    }
  });

})();
