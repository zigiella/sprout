/* Sprout landing-demo · try/pollen — primera versión funcional */

(function () {
  const $ = id => document.getElementById(id);
  const ta = $("transcript");
  const pipe = $("pollen-pipeline");
  const out = $("patch-output");

  const SAMPLES = {
    "es-clear": "Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos.",
    "en-clear": "I'll be back Friday. Plot B takes drier than you think — water it a bit less.",
    "ambiguous": "uhm pues yo qué sé"
  };

  document.querySelectorAll("[data-sample]").forEach(btn => {
    btn.addEventListener("click", () => {
      ta.value = SAMPLES[btn.dataset.sample] || "";
      ta.focus();
    });
  });

  async function pipelineStep(label, ms) {
    pipe.textContent = `pollen: ${label}`;
    return new Promise(r => setTimeout(r, ms));
  }

  $("pollen-form").addEventListener("submit", async ev => {
    ev.preventDefault();
    const transcript = ta.value.trim();

    out.textContent = "...";
    $("pollen-rationale-es").textContent = "";
    $("pollen-rationale-en").textContent = "";

    await pipelineStep("listening...", 350);
    await pipelineStep("compiling (Gemma 4 E4B)...", 500);
    await pipelineStep("validating schema + hard limits...", 350);

    try {
      const r = await window.SproutAPI.pollenCompile(transcript);

      if (r.action === "REFUSE_RETRY") {
        pipe.innerHTML = `<span class="status-pill alert">REFUSE_RETRY</span> ${r.reason}`;
        out.textContent = JSON.stringify({
          action: r.action,
          reason: r.reason,
          message_to_farmer: { es: r.message_es, en: r.message_en },
          transcript
        }, null, 2);
        $("pollen-rationale-es").textContent = r.message_es;
        $("pollen-rationale-en").textContent = r.message_en;
        return;
      }

      pipe.innerHTML = `<span class="status-pill ok">${r.action}</span> ${r.reason} · sending to Rhizome...`;
      out.textContent = JSON.stringify({
        action: r.action,
        reason: r.reason,
        mission_patch: r.mission_patch,
        valid_until_h: r.valid_until_h,
        policy_origin: "pollen-visit"
      }, null, 2);
      $("pollen-rationale-es").textContent = r.rationale_es;
      $("pollen-rationale-en").textContent = r.rationale_en;
    } catch (err) {
      pipe.innerHTML = `<span class="status-pill alert">ERROR</span> ${err}`;
      out.textContent = String(err);
    }
  });

})();
