// Meristem-nodo UI — internacionalización ligera (ES + EN, default ES).
//
// Sin dependencias. Diccionario plano por idioma. Función t(key, params)
// busca el string + interpola placeholders {nombre}. Persiste preferencia
// del usuario en localStorage bajo "meristem.locale".

(function () {
  "use strict";

  const STRINGS = {
    es: {
      // Topbar
      "topbar.brand": "Sprout · Meristem-nodo",
      "topbar.llm_real": "LLM: Real",
      "topbar.llm_stub": "LLM: Stub",
      "topbar.llm_loading": "LLM: …",
      "topbar.pollen_disconnected": "Pollen: desconectado",
      "topbar.pollen_connected": "Pollen: {id}",

      // Zona 1
      "zone1.title": "Tu parcela hoy",
      "zone1.empty": "Aún no has recibido ninguna visita de Pollen. Cuando llegue la primera, esta pantalla se actualizará.",
      "zone1.last_sync": "Última sync: {when}",
      "zone1.trazabilidad_label": "Reglas aplicadas:",
      "zone1.card.no_mode": "—",

      // Zona 2
      "zone2.title": "Sincronización con Pollen",
      "zone2.status_disconnected": "Pollen no detectado",
      "zone2.status_connected": "Pollen {id} conectado · {when}",
      "zone2.btn_recoger": "Recoger visitas",
      "zone2.btn_cargar": "Cargar policies",
      "zone2.meta_online": "online",
      "zone2.meta_offline": "offline",
      "zone2.progress_in_progress": "{label} en curso…",
      "zone2.progress_sent": "{label} enviado · trace {trace}",
      "zone2.progress_error": "Error: {msg}",
      "zone2.label_recoger": "Recoger visitas",
      "zone2.label_cargar": "Cargar policies",

      // Zona 3
      "zone3.title": "Operaciones recientes",
      "zone3.empty": "Sin eventos todavía.",

      // Zona 4
      "zone4.title": "Visitas recibidas",
      "zone4.col_time": "Hora",
      "zone4.col_target": "Rhizome",
      "zone4.col_pollen": "Pollen",
      "zone4.col_reason": "Resultado",
      "zone4.empty": "Sin visitas todavía.",
      "zone4.meta_count": "{shown} de {total}",

      // Zona 5
      "zone5.title": "Políticas emitidas",
      "zone5.col_time": "Emitida",
      "zone5.col_target": "Rhizome",
      "zone5.col_mode": "Modo",
      "zone5.col_validity": "Válida hasta",
      "zone5.col_rationale": "Rationale técnico",
      "zone5.empty": "Sin policies todavía.",
      "zone5.meta_count": "{shown} de {total}",
      "zone5.validity_prefix": "vál. ",

      // Footer
      "footer.text": "Meristem {id} v{version} · slow brain doméstico",

      // Reason codes (label corto + frase)
      "rc.STABLE_BUNDLE.tag": "ESTABLE",
      "rc.STABLE_BUNDLE.text": "Tu Rhizome funciona con normalidad.",
      "rc.EVIDENCE_LOW_CONFIDENCE.tag": "PRUDENCIA",
      "rc.EVIDENCE_LOW_CONFIDENCE.text": "Datos ambiguos en la última visita.",
      "rc.PERSISTENT_EMERGENCY.tag": "ALERTA",
      "rc.PERSISTENT_EMERGENCY.text": "Hay alerta persistente. Revisa.",
      "rc.HARD_LIMIT_DOMAIN.tag": "LÍMITE",
      "rc.HARD_LIMIT_DOMAIN.text": "Límite del firmware ESP32.",
      "rc.JURISDICTION_POLLEN.tag": "VÍA POLLEN",
      "rc.JURISDICTION_POLLEN.text": "Cambio puntual: usa Pollen.",
      "rc.null.tag": "Sin policy",
      "rc.null.text": "Aún no hay decisión.",

      // Time relativo
      "time.seconds_ago": "hace {n}s",
      "time.minutes_ago": "hace {n}m",
      "time.hours_ago": "hace {n}h",
      "time.days_ago": "hace {n}d",
      "time.dash": "—",

      // Toggle idioma
      "lang.switch_to_en": "EN",
      "lang.switch_to_es": "ES",
    },

    en: {
      // Topbar
      "topbar.brand": "Sprout · Meristem node",
      "topbar.llm_real": "LLM: Real",
      "topbar.llm_stub": "LLM: Stub",
      "topbar.llm_loading": "LLM: …",
      "topbar.pollen_disconnected": "Pollen: offline",
      "topbar.pollen_connected": "Pollen: {id}",

      // Zona 1
      "zone1.title": "Your plot today",
      "zone1.empty": "No visits from Pollen yet. The screen will update on first arrival.",
      "zone1.last_sync": "Last sync: {when}",
      "zone1.trazabilidad_label": "Rules applied:",
      "zone1.card.no_mode": "—",

      // Zona 2
      "zone2.title": "Sync with Pollen",
      "zone2.status_disconnected": "Pollen not detected",
      "zone2.status_connected": "Pollen {id} connected · {when}",
      "zone2.btn_recoger": "Pull visits",
      "zone2.btn_cargar": "Push policies",
      "zone2.meta_online": "online",
      "zone2.meta_offline": "offline",
      "zone2.progress_in_progress": "{label} in progress…",
      "zone2.progress_sent": "{label} sent · trace {trace}",
      "zone2.progress_error": "Error: {msg}",
      "zone2.label_recoger": "Pull visits",
      "zone2.label_cargar": "Push policies",

      // Zona 3
      "zone3.title": "Recent operations",
      "zone3.empty": "No events yet.",

      // Zona 4
      "zone4.title": "Visits received",
      "zone4.col_time": "Time",
      "zone4.col_target": "Rhizome",
      "zone4.col_pollen": "Pollen",
      "zone4.col_reason": "Result",
      "zone4.empty": "No visits yet.",
      "zone4.meta_count": "{shown} of {total}",

      // Zona 5
      "zone5.title": "Policies issued",
      "zone5.col_time": "Issued",
      "zone5.col_target": "Rhizome",
      "zone5.col_mode": "Mode",
      "zone5.col_validity": "Valid until",
      "zone5.col_rationale": "Technical rationale",
      "zone5.empty": "No policies yet.",
      "zone5.meta_count": "{shown} of {total}",
      "zone5.validity_prefix": "until ",

      // Footer
      "footer.text": "Meristem {id} v{version} · domestic slow brain",

      // Reason codes
      "rc.STABLE_BUNDLE.tag": "STABLE",
      "rc.STABLE_BUNDLE.text": "Your Rhizome is working normally.",
      "rc.EVIDENCE_LOW_CONFIDENCE.tag": "CAUTION",
      "rc.EVIDENCE_LOW_CONFIDENCE.text": "Ambiguous data in last visit.",
      "rc.PERSISTENT_EMERGENCY.tag": "ALERT",
      "rc.PERSISTENT_EMERGENCY.text": "Persistent alert. Please review.",
      "rc.HARD_LIMIT_DOMAIN.tag": "LIMIT",
      "rc.HARD_LIMIT_DOMAIN.text": "ESP32 firmware limit.",
      "rc.JURISDICTION_POLLEN.tag": "VIA POLLEN",
      "rc.JURISDICTION_POLLEN.text": "Point change: use Pollen.",
      "rc.null.tag": "No policy",
      "rc.null.text": "No decision yet.",

      // Time relativo
      "time.seconds_ago": "{n}s ago",
      "time.minutes_ago": "{n}m ago",
      "time.hours_ago": "{n}h ago",
      "time.days_ago": "{n}d ago",
      "time.dash": "—",

      // Toggle idioma
      "lang.switch_to_en": "EN",
      "lang.switch_to_es": "ES",
    },
  };

  const STORAGE_KEY = "meristem.locale";
  const SUPPORTED_LOCALES = ["es", "en"];
  const DEFAULT_LOCALE = "es";

  function getLocale() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (SUPPORTED_LOCALES.includes(saved)) return saved;
    } catch (e) { /* localStorage no disponible (modo privado, etc.) */ }
    return DEFAULT_LOCALE;
  }

  function setLocale(locale) {
    if (!SUPPORTED_LOCALES.includes(locale)) return;
    try {
      localStorage.setItem(STORAGE_KEY, locale);
    } catch (e) { /* ignorar */ }
    window.dispatchEvent(new CustomEvent("meristem:localechange", {
      detail: { locale },
    }));
  }

  function interpolate(template, params) {
    if (!params) return template;
    return template.replace(/\{(\w+)\}/g, (m, key) => {
      return params[key] != null ? String(params[key]) : m;
    });
  }

  function t(key, params) {
    const locale = getLocale();
    const dict = STRINGS[locale] || STRINGS[DEFAULT_LOCALE];
    const template = dict[key] != null ? dict[key] : key;
    return interpolate(template, params);
  }

  // API global
  window.Meristem = window.Meristem || {};
  window.Meristem.i18n = {
    t,
    getLocale,
    setLocale,
    SUPPORTED_LOCALES,
    DEFAULT_LOCALE,
  };
})();
