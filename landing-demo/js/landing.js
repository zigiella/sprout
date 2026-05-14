// Sprout landing · interactive demo for the home page.
// Uses the deterministic mock functions from js/api.js.

(function () {
  const output = document.getElementById('output');

  const demos = {
    rhizome: async () => {
      output.textContent = 'Rhizome reading local state...\n';
      const state = {
        soil_pct: 18,
        tank_pct: 65,
        heartbeat_age_s: 4
      };
      const result = await rhizomeDecideMock(state);
      output.textContent = JSON.stringify(result, null, 2);
    },

    pollen: async () => {
      output.textContent = 'Pollen compiling voice...\n';
      const transcript = "Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos.";
      const result = await pollenCompileMock(transcript);
      output.textContent = JSON.stringify(result, null, 2);
    },

    meristem: async () => {
      output.textContent = 'Meristem evaluating bundle...\n';
      const bundle = {
        recent_decisions: [
          { action: 'irrigate', confidence: 0.88 },
          { action: 'skip', confidence: 0.91 },
          { action: 'block', confidence: 0.95 }
        ],
        avg_confidence: 0.91
      };
      const result = await meristemEvaluateMock(bundle);
      output.textContent = JSON.stringify(result, null, 2);
    }
  };

  document.querySelectorAll('[data-demo]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const which = btn.getAttribute('data-demo');
      if (demos[which]) {
        btn.disabled = true;
        const originalText = btn.textContent;
        btn.textContent = 'Running...';
        try {
          await demos[which]();
        } finally {
          btn.disabled = false;
          btn.textContent = originalText;
        }
      }
    });
  });
})();
