// Pollen — screens

const { useState, useEffect, useRef, useMemo } = React;

// ───────────────────────────────────────────────
// Mock data
// ───────────────────────────────────────────────
const MOCK_RHIZOMES = [
  {
    id: 'RHIZOME_01', plot: 'PLOT_01', state: 'connected',
    lastSeen: 2, soilA: 31, soilB: 28, tank: 30,
    activeMission: { horizon_h: 72, dry: 25, budget: 900 },
    lastDecision: { kind: 'WATER', s: 12, time: '08:42', soil: 29, threshold: 34, safe: true }
  },
  {
    id: 'RHIZOME_02', plot: 'PLOT_02', state: 'stale',
    lastSeen: 180, soilA: 18, soilB: 22, tank: 12,
  },
  {
    id: 'RHIZOME_03', plot: 'PLOT_03 · greenhouse', state: 'offline',
    lastSeen: 1440, soilA: null, soilB: null, tank: null,
  },
];

const MOCK_RECEIPTS_KEYS = [
  { kind: 'water', s: 12, time: '08:42', plot: 'PLOT_01', soil: 29, threshold: 34, budget: 240, reason: 'below_threshold' },
  { kind: 'skip',  time: '06:15', plot: 'PLOT_01', soil: 38, threshold: 34, reason: 'above_threshold' },
  { kind: 'water', s: 18, time: 'yest 14:00', plot: 'PLOT_01', soil: 27, threshold: 34, budget: 480, reason: 'below_threshold' },
  { kind: 'blocked', time: 'yest 13:10', plot: 'PLOT_01', reason: 'budget_cap_reached' },
  { kind: 'updated', time: 'yest 11:00', plot: 'PLOT_01', reason: 'mission_patch_applied' },
  { kind: 'water', s: 10, time: 'yest 09:30', plot: 'PLOT_01', soil: 28, threshold: 34, budget: 660, reason: 'below_threshold' },
  { kind: 'skip',  time: 'yest 22:00', plot: 'PLOT_01', soil: 41, threshold: 34, reason: 'above_threshold' },
  { kind: 'expired', time: '2 days ago', plot: 'PLOT_01', reason: 'context_ttl_expired' },
];

const RECEIPT_LABEL = (kind, copy) => ({
  water: copy.receiptWater, skip: copy.receiptSkip, defer: copy.receiptDefer,
  blocked: copy.receiptBlocked, updated: copy.receiptUpdated, expired: copy.receiptExpired,
}[kind]);

const RECEIPT_REASON_TXT = (key, lang) => ({
  below_threshold:    { en: 'Below threshold, safe envelope valid.', es: 'Por debajo del umbral, envoltura segura válida.' },
  above_threshold:    { en: 'Soil above threshold. No action needed.', es: 'Suelo por encima del umbral. Ninguna acción.' },
  budget_cap_reached: { en: 'Daily budget cap reached. Physical layer refused further action.', es: 'Presupuesto diario alcanzado. La capa física rechazó más acción.' },
  mission_patch_applied: { en: 'MissionPatch applied: dry threshold 35 → 25.', es: 'MissionPatch aplicado: umbral seco 35 → 25.' },
  context_ttl_expired:{ en: 'WeatherDigest TTL expired. Context rejected.', es: 'TTL de WeatherDigest caducado. Contexto rechazado.' },
}[key]?.[lang] || '');

// ───────────────────────────────────────────────
// Header used across screens
// ───────────────────────────────────────────────
function ScreenHeader({ title, subtitle, theme, onBack, lang, onLangToggle, onOutdoorToggle, outdoor, right }) {
  return (
    <div style={{
      padding: '14px 18px 12px',
      borderBottom: `1px solid ${theme.borderSubtle}`,
      background: theme.bg,
      display: 'flex', alignItems: 'center', gap: 12,
    }}>
      {onBack && (
        <button onClick={onBack} style={{
          width: 36, height: 36, borderRadius: 10, border: `1px solid ${theme.border}`,
          background: theme.surface, cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: POLLEN_FONT_MONO, color: theme.humus, fontSize: 16,
        }}>←</button>
      )}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontFamily: POLLEN_FONT_SANS, fontSize: 20, fontWeight: 700,
          color: theme.humus, lineHeight: 1.2, letterSpacing: -0.2,
        }}>{title}</div>
        {subtitle && <div style={{
          fontFamily: POLLEN_FONT_MONO, fontSize: 11.5, color: theme.humusDim, marginTop: 2,
        }}>{subtitle}</div>}
      </div>
      {right}
      {onLangToggle && (
        <button onClick={onLangToggle} style={{
          height: 32, padding: '0 10px', borderRadius: 8,
          border: `1px solid ${theme.border}`, background: theme.surface,
          fontFamily: POLLEN_FONT_MONO, fontSize: 11, fontWeight: 600,
          color: theme.humus, cursor: 'pointer', letterSpacing: 0.5,
        }}>{lang.toUpperCase()}</button>
      )}
    </div>
  );
}

// ───────────────────────────────────────────────
// HOME
// ───────────────────────────────────────────────
function HomeScreen({ theme, copy, lang, onLangToggle, onOpenRhizome, onOpenSync, layout }) {
  const rhizomes = MOCK_RHIZOMES;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100%', background: theme.bg }}>
      <ScreenHeader
        title={copy.appTitle}
        subtitle={copy.appSubtitle}
        theme={theme}
        lang={lang}
        onLangToggle={onLangToggle}
      />

      <div style={{ padding: '16px 18px 24px', flex: 1, display: 'flex', flexDirection: 'column', gap: 18 }}>
        {/* Status strip */}
        <div style={{
          display: 'flex', gap: 8, alignItems: 'center',
          padding: '10px 12px',
          background: theme.surfaceAlt,
          border: `1px solid ${theme.border}`,
          borderRadius: 10,
        }}>
          <SeedPulse color={theme.moss} />
          <span style={{
            fontFamily: POLLEN_FONT_MONO, fontSize: 11.5, color: theme.humus,
          }}>{copy.everyEventReceipt}</span>
        </div>

        {/* Nearby Rhizomes */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 10 }}>
            <SectionLabel theme={theme}>{copy.nearbyRhizomes}</SectionLabel>
            <span style={{
              fontFamily: POLLEN_FONT_MONO, fontSize: 11, color: theme.humusDim,
            }}>{rhizomes.length} found</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {rhizomes.map(r => (
              <RhizomeCard
                key={r.id} rhizome={r} theme={theme} copy={copy} lang={lang}
                onClick={() => r.state !== 'offline' && onOpenRhizome(r)}
                layout={layout}
              />
            ))}
          </div>
        </div>

        {/* Slow brain */}
        <div>
          <SectionLabel theme={theme}>{copy.slowBrain}</SectionLabel>
          <button onClick={onOpenSync} style={{
            width: '100%', textAlign: 'left',
            background: theme.surface, border: `1px solid ${theme.border}`,
            borderRadius: 12, padding: 16, cursor: 'pointer',
            display: 'flex', alignItems: 'center', gap: 14,
          }}>
            <div style={{
              width: 40, height: 40, borderRadius: 10,
              background: theme.surfaceAlt, border: `1px solid ${theme.border}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: POLLEN_FONT_MONO, color: theme.moss, fontSize: 18,
            }}>◇</div>
            <div style={{ flex: 1, minWidth: 0, textAlign: 'left' }}>
              <MonoID theme={theme}>MERISTEM_HOME</MonoID>
              <div style={{
                fontFamily: POLLEN_FONT_SANS, fontSize: 13, color: theme.humusDim, marginTop: 2,
              }}>{copy.meristemSub}</div>
            </div>
            <StatusChip kind="ai" label={copy.syncing} theme={theme} mono />
          </button>
        </div>

        <div style={{ flex: 1 }} />

        <div style={{
          fontFamily: POLLEN_FONT_MONO, fontSize: 10.5, color: theme.humusDim, textAlign: 'center',
        }}>{copy.physicalPrevails}</div>
      </div>
    </div>
  );
}

function RhizomeCard({ rhizome, theme, copy, onClick, lang, layout }) {
  const r = rhizome;
  const stateMap = {
    connected: copy.connected, offline: copy.offline, stale: copy.stale, error: copy.error
  };
  const lastSeenStr = (m) => {
    if (m < 60) return `${m} min ago`;
    if (m < 1440) return `${Math.floor(m/60)}h ago`;
    return `${Math.floor(m/1440)}d ago`;
  };
  const lastSeenStrEs = (m) => {
    if (m < 60) return `hace ${m} min`;
    if (m < 1440) return `hace ${Math.floor(m/60)}h`;
    return `hace ${Math.floor(m/1440)}d`;
  };
  const seenTxt = lang === 'es' ? lastSeenStrEs(r.lastSeen) : lastSeenStr(r.lastSeen);
  const isOffline = r.state === 'offline';

  if (layout === 'compact') {
    return (
      <button onClick={onClick} disabled={isOffline} style={{
        width: '100%', textAlign: 'left', cursor: isOffline ? 'not-allowed' : 'pointer',
        background: theme.surface, border: `1px solid ${theme.border}`,
        borderRadius: 10, padding: '12px 14px',
        display: 'flex', alignItems: 'center', gap: 12,
        opacity: isOffline ? 0.55 : 1,
      }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <MonoID theme={theme} size={13}>{r.id}</MonoID>
            <StatusChip kind={r.state} label={stateMap[r.state]} theme={theme} mono />
          </div>
          <div style={{ fontFamily: POLLEN_FONT_MONO, fontSize: 11, color: theme.humusDim, marginTop: 2 }}>
            {r.plot} · {seenTxt}
            {r.soilA != null && ` · soil ${r.soilA}% · tank ${r.tank}%`}
          </div>
        </div>
        <span style={{ color: theme.humusDim, fontFamily: POLLEN_FONT_MONO }}>›</span>
      </button>
    );
  }

  return (
    <button onClick={onClick} disabled={isOffline} style={{
      width: '100%', textAlign: 'left', cursor: isOffline ? 'not-allowed' : 'pointer',
      background: theme.surface, border: `1px solid ${theme.border}`,
      borderRadius: 12, padding: 16,
      display: 'flex', flexDirection: 'column', gap: 12,
      opacity: isOffline ? 0.55 : 1,
      position: 'relative',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
        <div>
          <MonoID theme={theme} size={14}>{r.id}</MonoID>
          <div style={{
            fontFamily: POLLEN_FONT_SANS, fontSize: 13, color: theme.humusDim, marginTop: 2,
          }}>{r.plot} · {seenTxt}</div>
        </div>
        <StatusChip kind={r.state} label={stateMap[r.state]} theme={theme} mono />
      </div>

      {!isOffline && (
        <div style={{
          display: 'flex', gap: 10, paddingTop: 8,
          borderTop: `1px solid ${theme.borderSubtle}`,
        }}>
          <MiniMetric label={lang==='es'?'suelo':'soil'} value={r.soilA != null ? r.soilA : '—'} unit="%" theme={theme} />
          <MiniMetric label={lang==='es'?'depósito':'tank'} value={r.tank != null ? r.tank : '—'} unit="%" theme={theme} danger={r.tank != null && r.tank < 20} />
        </div>
      )}
    </button>
  );
}

function MiniMetric({ label, value, unit, theme, danger }) {
  return (
    <div style={{
      flex: 1, padding: '6px 10px', background: theme.surfaceAlt, borderRadius: 6,
      display: 'flex', alignItems: 'baseline', gap: 6,
    }}>
      <span style={{
        fontFamily: POLLEN_FONT_MONO, fontSize: 10, color: theme.humusDim, textTransform: 'uppercase',
      }}>{label}</span>
      <span style={{
        fontFamily: POLLEN_FONT_MONO, fontSize: 13, fontWeight: 600,
        color: danger ? theme.blocked : theme.humus,
      }}>{value}{unit}</span>
    </div>
  );
}

// ───────────────────────────────────────────────
// RHIZOME STATUS
// ───────────────────────────────────────────────
function RhizomeStatusScreen({ theme, copy, lang, onBack, rhizome, onAction }) {
  const r = rhizome;
  return (
    <div style={{ background: theme.bg, minHeight: '100%' }}>
      <ScreenHeader
        title={r.plot}
        subtitle={`${r.id} · ${copy.connected.toLowerCase()} · ${copy.lastUpdate} 08:42`}
        theme={theme} onBack={onBack}
      />
      <div style={{ padding: '16px 18px 32px', display: 'flex', flexDirection: 'column', gap: 16 }}>

        {/* Telemetry trio */}
        <div>
          <SectionLabel theme={theme}>telemetry · {r.id}</SectionLabel>
          <div style={{ display: 'flex', gap: 8 }}>
            <TelemetryTile label={copy.tank} value={r.tank} unit="%" sub={copy.usableWater}
              bar={r.tank} theme={theme} color={theme.water} />
            <TelemetryTile label={copy.soilA} value={r.soilA} unit="%" sub={`${copy.threshold} 25%`}
              bar={r.soilA} theme={theme} color={theme.moss} />
            <TelemetryTile label={copy.soilB} value={r.soilB} unit="%" sub={`${copy.threshold} 25%`}
              bar={r.soilB} theme={theme} color={theme.moss} />
          </div>
        </div>

        {/* Active mission */}
        <Card theme={theme} accent={theme.seed}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <SectionLabel theme={theme}>{copy.activeMission}</SectionLabel>
            <StatusChip kind="ai" label="ai · compiled" theme={theme} mono />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', rowGap: 4, columnGap: 12,
              fontFamily: POLLEN_FONT_MONO, fontSize: 12.5, color: theme.humus }}>
            <span style={{ color: theme.humusDim }}>horizon_h</span><span>{r.activeMission.horizon_h}</span>
            <span style={{ color: theme.humusDim }}>soil_thresholds.dry</span><span>35 → {r.activeMission.dry}</span>
            <span style={{ color: theme.humusDim }}>budget_cap_ml</span><span>{r.activeMission.budget}</span>
            <span style={{ color: theme.humusDim }}>operator_note</span><span style={{ color: theme.moss }}>preserved</span>
          </div>
        </Card>

        {/* Last decision */}
        <Card theme={theme}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 8 }}>
            <SectionLabel theme={theme}>{copy.lastDecision}</SectionLabel>
            <span style={{ fontFamily: POLLEN_FONT_MONO, fontSize: 11, color: theme.humusDim }}>{r.lastDecision.time}</span>
          </div>
          <div style={{
            fontFamily: POLLEN_FONT_MONO, fontSize: 14, fontWeight: 600, color: theme.water, marginBottom: 4,
          }}>WATER · {r.lastDecision.s}s</div>
          <div style={{
            fontFamily: POLLEN_FONT_MONO, fontSize: 12, color: theme.humusDim,
          }}>soil {r.lastDecision.soil}% · threshold {r.lastDecision.threshold}%</div>
          <div style={{
            fontFamily: POLLEN_FONT_SANS, fontSize: 13, color: theme.ok, marginTop: 6,
            display: 'flex', alignItems: 'center', gap: 6,
          }}><Dot color={theme.ok} /> {copy.safeEnvelope}</div>
        </Card>

        {/* Primary action */}
        <PrimaryButton theme={theme} onClick={() => onAction('visit')}>
          {copy.startVisit} →
        </PrimaryButton>

        {/* Secondary actions */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          <SecondaryAction theme={theme} onClick={() => onAction('ask')}>{copy.askWhatHappened}</SecondaryAction>
          <SecondaryAction theme={theme} onClick={() => onAction('mission')}>{copy.createMission}</SecondaryAction>
          <SecondaryAction theme={theme} onClick={() => onAction('audit')}>{copy.auditVisit}</SecondaryAction>
          <SecondaryAction theme={theme} onClick={() => onAction('ferry')}>{copy.carryContext}</SecondaryAction>
        </div>
        <SecondaryAction theme={theme} onClick={() => onAction('ledger')} full>{copy.viewLog} →</SecondaryAction>
      </div>
    </div>
  );
}

function SecondaryAction({ theme, onClick, children, full }) {
  return (
    <button onClick={onClick} style={{
      gridColumn: full ? '1 / -1' : 'auto',
      height: 44, padding: '0 14px',
      background: 'transparent', border: `1px solid ${theme.border}`,
      borderRadius: 10, cursor: 'pointer',
      fontFamily: POLLEN_FONT_SANS, fontSize: 13.5, fontWeight: 600,
      color: theme.humus, textAlign: 'center',
    }}>{children}</button>
  );
}

// ───────────────────────────────────────────────
// VISIT CONSOLE
// ───────────────────────────────────────────────
function VisitConsoleScreen({ theme, copy, lang, onBack, rhizome, onSubScreen }) {
  // step state
  const [step, setStep] = useState(0);
  const steps = [
    { label: copy.connectToRhizome,   sub: 'BLE · 2.4 GHz · 0.4s' },
    { label: copy.downloadSnapshot,   sub: '6.2 KB · 312 ms' },
    { label: copy.readReceipts,       sub: '8 receipts · 24h window' },
    { label: copy.askAuditCompile,    sub: 'choose action' },
    { label: copy.sendPatch,          sub: 'awaiting compose' },
    { label: copy.receiveAck,         sub: 'pending' },
  ];

  useEffect(() => {
    if (step < 3) {
      const t = setTimeout(() => setStep(s => s + 1), 900);
      return () => clearTimeout(t);
    }
  }, [step]);

  return (
    <div style={{ background: theme.bg, minHeight: '100%' }}>
      <ScreenHeader
        title={copy.visitConsole}
        subtitle={`${rhizome.id} · ${rhizome.plot}`}
        theme={theme} onBack={onBack}
      />
      <div style={{ padding: '16px 18px 32px', display: 'flex', flexDirection: 'column', gap: 18 }}>
        <Card theme={theme} padding={4}>
          <div style={{ padding: '12px 14px 4px' }}>
            <SectionLabel theme={theme}>visit checklist</SectionLabel>
          </div>
          <div style={{ padding: '0 14px 8px' }}>
            {steps.map((s, i) => (
              <SyncStep
                key={i}
                label={s.label}
                sub={i <= step ? s.sub : ''}
                status={i < step ? 'done' : i === step ? 'active' : 'pending'}
                theme={theme}
              />
            ))}
          </div>
        </Card>

        {step >= 3 && (
          <>
            <SectionLabel theme={theme}>actions</SectionLabel>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <ActionTile theme={theme} glyph="?" label={copy.askWhatHappened} onClick={() => onSubScreen('ask')} />
              <ActionTile theme={theme} glyph="◇" label={copy.createMission} onClick={() => onSubScreen('mission')} accent={theme.seed} />
              <ActionTile theme={theme} glyph="✓" label={copy.auditVisit} onClick={() => onSubScreen('audit')} />
              <ActionTile theme={theme} glyph="⇄" label={copy.carryContext} onClick={() => onSubScreen('ferry')} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function ActionTile({ theme, glyph, label, onClick, accent }) {
  return (
    <button onClick={onClick} style={{
      background: theme.surface, border: `1px solid ${theme.border}`,
      borderTop: accent ? `3px solid ${accent}` : `1px solid ${theme.border}`,
      borderRadius: 12, padding: 14, cursor: 'pointer',
      display: 'flex', flexDirection: 'column', gap: 10, alignItems: 'flex-start',
      textAlign: 'left', minHeight: 84,
    }}>
      <div style={{
        width: 28, height: 28, borderRadius: 6,
        background: theme.surfaceAlt, border: `1px solid ${theme.border}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: POLLEN_FONT_MONO, fontSize: 14, color: accent || theme.humus,
      }}>{glyph}</div>
      <div style={{ fontFamily: POLLEN_FONT_SANS, fontSize: 13, fontWeight: 600, color: theme.humus, lineHeight: 1.3 }}>
        {label}
      </div>
    </button>
  );
}

Object.assign(window, {
  HomeScreen, RhizomeStatusScreen, VisitConsoleScreen,
  ScreenHeader, RhizomeCard, MOCK_RHIZOMES, MOCK_RECEIPTS_KEYS,
  RECEIPT_LABEL, RECEIPT_REASON_TXT, ActionTile, SecondaryAction, MiniMetric,
});
