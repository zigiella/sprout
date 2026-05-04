// Pollen — secondary screens (Mission compiler, Ask, Audit, Ferry, Ledger, Sync, Tech)

const { useState: useState2, useEffect: useEffect2, useRef: useRef2 } = React;

// ───────────────────────────────────────────────
// MISSION COMPILER
// ───────────────────────────────────────────────
function MissionCompilerScreen({ theme, copy, lang, onBack, onAck, variant = 'voice' }) {
  const [phase, setPhase] = useState2('idle'); // idle | listening | compiling | validating | valid | sent | acked
  const [text, setText] = useState2('');
  const [showJurisdiction, setShowJurisdiction] = useState2(false);

  const sampleEs = "Vuelvo el viernes. Esta planta aguanta más seca, pero no quiero que muera. Reduce un poco el riego pero deja margen.";
  const sampleEn = "I'm back on Friday. This plant can handle drier soil, but I don't want it to die. Reduce watering a bit, leave headroom.";

  const startVoice = () => {
    setPhase('listening');
    setText('');
    let i = 0;
    const sample = lang === 'es' ? sampleEs : sampleEn;
    const tick = () => {
      if (i < sample.length) {
        setText(sample.slice(0, i + 1));
        i += 2;
        setTimeout(tick, 35);
      } else {
        setText(sample);
        setTimeout(() => setPhase('compiling'), 250);
        setTimeout(() => setPhase('validating'), 1300);
        setTimeout(() => setPhase('valid'), 2400);
      }
    };
    tick();
  };

  const sendPatch = () => {
    setPhase('sent');
    setTimeout(() => setPhase('acked'), 1100);
    setTimeout(() => onAck && onAck(), 2400);
  };

  const reset = () => { setPhase('idle'); setText(''); };

  return (
    <div style={{ background: theme.bg, minHeight: '100%' }}>
      <ScreenHeader
        title={copy.createMission}
        subtitle="RHIZOME_01 · pollen.compose"
        theme={theme} onBack={onBack}
      />

      <div style={{ padding: '16px 18px 32px', display: 'flex', flexDirection: 'column', gap: 16 }}>

        {/* Voice / text input */}
        {variant === 'voice' && (
          <Card theme={theme} padding={0} style={{ overflow: 'hidden' }}>
            <div style={{
              padding: '14px 16px',
              borderBottom: `1px solid ${theme.borderSubtle}`,
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            }}>
              <SectionLabel theme={theme}>{copy.voiceNote}</SectionLabel>
              {phase === 'listening' && <PhasePill phase={copy.listening} theme={theme} />}
              {phase === 'compiling' && <PhasePill phase={copy.compiling} theme={theme} />}
              {phase === 'validating' && <PhasePill phase={copy.validating} theme={theme} />}
              {phase === 'valid' && <StatusChip kind="validated" label={copy.validated} theme={theme} mono />}
              {phase === 'sent' && <StatusChip kind="syncing" label={copy.syncing} theme={theme} mono />}
              {phase === 'acked' && <StatusChip kind="validated" label={copy.ackReceived} theme={theme} mono />}
            </div>
            <div style={{
              padding: '20px 16px',
              minHeight: 120,
              background: theme.surfaceAlt + '60',
              fontFamily: POLLEN_FONT_SANS, fontSize: 15, lineHeight: 1.55,
              color: theme.humus,
              fontStyle: text ? 'normal' : 'italic',
              opacity: text ? 1 : 0.5,
              position: 'relative',
            }}>
              {text || copy.speakOrType}
              {phase === 'listening' && <Caret theme={theme} />}
            </div>

            {/* Waveform area */}
            {phase === 'listening' && <Waveform theme={theme} />}

            <div style={{ padding: 12, display: 'flex', gap: 8, borderTop: `1px solid ${theme.borderSubtle}` }}>
              {phase === 'idle' && (
                <PrimaryButton theme={theme} kind="primary" onClick={startVoice}
                  icon={<MicGlyph color={theme.bg} />}>{copy.speak}</PrimaryButton>
              )}
              {(phase === 'listening' || phase === 'compiling' || phase === 'validating') && (
                <PrimaryButton theme={theme} kind="ghost" onClick={reset}>{copy.cancel}</PrimaryButton>
              )}
              {phase === 'valid' && (
                <>
                  <PrimaryButton theme={theme} kind="secondary" onClick={reset} full={false}>{copy.discard}</PrimaryButton>
                  <PrimaryButton theme={theme} kind="ai" onClick={sendPatch}>
                    {copy.send} →
                  </PrimaryButton>
                </>
              )}
              {phase === 'sent' && <PrimaryButton theme={theme} kind="primary" loading>{copy.send}…</PrimaryButton>}
              {phase === 'acked' && (
                <div style={{ flex: 1, fontFamily: POLLEN_FONT_SANS, fontSize: 13, color: theme.ok, textAlign: 'center', alignSelf: 'center' }}>
                  ✓ {copy.missionAcknowledged}
                </div>
              )}
            </div>
          </Card>
        )}

        {variant === 'text' && (
          <Card theme={theme} padding={0}>
            <div style={{ padding: '14px 16px', borderBottom: `1px solid ${theme.borderSubtle}` }}>
              <SectionLabel theme={theme}>{copy.voiceNote}</SectionLabel>
            </div>
            <textarea
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder={copy.speakOrType}
              style={{
                width: '100%', minHeight: 130, border: 'none', resize: 'none',
                padding: '16px',
                fontFamily: POLLEN_FONT_SANS, fontSize: 15, lineHeight: 1.55,
                background: 'transparent', color: theme.humus,
                outline: 'none', boxSizing: 'border-box',
              }}
            />
            <div style={{ padding: 12, display: 'flex', gap: 8, borderTop: `1px solid ${theme.borderSubtle}` }}>
              <PrimaryButton theme={theme} kind="ai" onClick={() => {
                setPhase('compiling');
                setTimeout(() => setPhase('validating'), 800);
                setTimeout(() => setPhase('valid'), 1700);
              }} disabled={!text || phase !== 'idle'}>
                {phase === 'idle' ? copy.compile : phase === 'compiling' ? copy.compiling+'…' : phase === 'validating' ? copy.validating+'…' : copy.review}
              </PrimaryButton>
            </div>
          </Card>
        )}

        {/* Compiled patch */}
        {(phase === 'valid' || phase === 'sent' || phase === 'acked') && (
          <Card theme={theme} accent={theme.seed}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <SectionLabel theme={theme}>{copy.compiledPatch}</SectionLabel>
              <MonoID theme={theme} size={10} color={theme.humusDim}>schema v0.3</MonoID>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', rowGap: 6, columnGap: 12,
                fontFamily: POLLEN_FONT_MONO, fontSize: 12.5, color: theme.humus }}>
              <span style={{ color: theme.humusDim }}>horizon_h</span><span>72</span>
              <span style={{ color: theme.humusDim }}>soil_thresholds.dry</span>
                <span><s style={{ color: theme.humusDim }}>35</s> → <strong>25</strong></span>
              <span style={{ color: theme.humusDim }}>budget_cap_ml</span><span>900</span>
              <span style={{ color: theme.humusDim }}>watering_window</span><span>06:00–10:00</span>
              <span style={{ color: theme.humusDim }}>operator_note</span>
                <span style={{ color: theme.moss }}>preserved (es)</span>
            </div>
          </Card>
        )}

        {/* Status */}
        {phase === 'valid' && (
          <JurisdictionBanner kind="ai" theme={theme}>{copy.missionValidated}</JurisdictionBanner>
        )}
        {phase === 'acked' && (
          <JurisdictionBanner kind="ai" theme={theme}>{copy.missionAcknowledged}</JurisdictionBanner>
        )}

        {/* Jurisdiction reminder */}
        {phase === 'idle' && (
          <button
            onClick={() => setShowJurisdiction(s => !s)}
            style={{
              all: 'unset', cursor: 'pointer',
              fontFamily: POLLEN_FONT_MONO, fontSize: 11, color: theme.humusDim,
              textAlign: 'center', padding: 6,
            }}
          >▾ jurisdiction · safety</button>
        )}
        {showJurisdiction && phase === 'idle' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <JurisdictionBanner kind="warning" theme={theme}>{copy.pollenJurisdiction}</JurisdictionBanner>
            <JurisdictionBanner kind="physical" theme={theme}>{copy.safetyJurisdiction}</JurisdictionBanner>
          </div>
        )}
      </div>
    </div>
  );
}

function PhasePill({ phase, theme }) {
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '4px 10px', borderRadius: 100,
      background: theme.seed + '40', border: `1px solid ${theme.moss}`,
      fontFamily: POLLEN_FONT_MONO, fontSize: 11, color: '#3a5610',
    }}>
      <SeedPulse color="#3a5610" /> {phase}…
    </span>
  );
}

function Caret({ theme }) {
  return <span style={{
    display: 'inline-block', width: 2, height: 18, background: theme.humus,
    verticalAlign: 'text-bottom', marginLeft: 2,
    animation: 'pollenBlink 1s steps(2) infinite',
  }} />;
}

function MicGlyph({ color = '#fff' }) {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14">
      <rect x="5.5" y="2" width="3" height="6.5" rx="1.5" fill={color} />
      <path d="M3 7c0 2 1.8 3.5 4 3.5S11 9 11 7" stroke={color} strokeWidth="1.4" fill="none" strokeLinecap="round" />
      <line x1="7" y1="10.5" x2="7" y2="12.5" stroke={color} strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}

function Waveform({ theme }) {
  const bars = Array.from({ length: 24 });
  return (
    <div style={{
      display: 'flex', gap: 3, alignItems: 'center', justifyContent: 'center',
      height: 32, padding: '0 16px', borderTop: `1px solid ${theme.borderSubtle}`,
    }}>
      {bars.map((_, i) => (
        <div key={i} style={{
          width: 3, background: theme.moss, borderRadius: 2,
          animation: `pollenWave 0.9s ease-in-out ${i * 0.05}s infinite alternate`,
        }} />
      ))}
    </div>
  );
}

// ───────────────────────────────────────────────
// ASK
// ───────────────────────────────────────────────
function AskScreen({ theme, copy, lang, onBack }) {
  return (
    <div style={{ background: theme.bg, minHeight: '100%' }}>
      <ScreenHeader title={copy.askWhatHappened} subtitle="RHIZOME_01 · explain.window=24h" theme={theme} onBack={onBack} />
      <div style={{ padding: '16px 18px 32px', display: 'flex', flexDirection: 'column', gap: 14 }}>

        <Card theme={theme}>
          <div style={{
            fontFamily: POLLEN_FONT_SANS, fontSize: 14, fontWeight: 600, color: theme.humus,
          }}>{copy.askPlaceholder}</div>
          <div style={{
            fontFamily: POLLEN_FONT_MONO, fontSize: 11, color: theme.humusDim, marginTop: 4,
          }}>asked 09:31 · {lang}</div>
        </Card>

        <Card theme={theme} accent={theme.seed}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
            <SectionLabel theme={theme}>{copy.sinceLastVisit}</SectionLabel>
            <StatusChip kind="ai" label="evidence-only" theme={theme} mono />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
            <BigStat theme={theme} value="2" label={copy.wateringEvents} color={theme.water} />
            <BigStat theme={theme} value="1" label={copy.skippedDecision} color={theme.humusDim} />
            <BigStat theme={theme} value="0" label={copy.blockedActions} color={theme.ok} />
          </div>
        </Card>

        <SectionLabel theme={theme}>receipts · 24h</SectionLabel>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {MOCK_RECEIPTS_KEYS.slice(0, 4).map((r, i) => (
            <ReceiptCard key={i}
              kind={RECEIPT_LABEL(r.kind, copy)}
              durationS={r.s} timestamp={r.time} plot={r.plot}
              evidence={r.soil != null ? `soil ${r.soil}% · threshold ${r.threshold}%${r.budget != null ? ` · budget left ${r.budget} ml` : ''}` : null}
              reason={RECEIPT_REASON_TXT(r.reason, lang)}
              theme={theme} copy={copy}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function BigStat({ theme, value, label, color }) {
  return (
    <div style={{
      padding: '12px 8px', textAlign: 'center',
      background: theme.surfaceAlt, borderRadius: 8, border: `1px solid ${theme.borderSubtle}`,
    }}>
      <div style={{ fontFamily: POLLEN_FONT_SANS, fontSize: 26, fontWeight: 700, color, lineHeight: 1 }}>{value}</div>
      <div style={{ fontFamily: POLLEN_FONT_MONO, fontSize: 10, color: theme.humusDim, marginTop: 4, lineHeight: 1.3 }}>{label}</div>
    </div>
  );
}

// ───────────────────────────────────────────────
// AUDIT
// ───────────────────────────────────────────────
function AuditScreen({ theme, copy, lang, onBack }) {
  const [obs, setObs] = useState2('');
  const [result, setResult] = useState2(null); // 'match' | 'conflict'

  const submit = (kind) => {
    setResult(kind);
  };

  return (
    <div style={{ background: theme.bg, minHeight: '100%' }}>
      <ScreenHeader title={copy.auditVisit} subtitle="RHIZOME_01 · validation.stamp" theme={theme} onBack={onBack} />
      <div style={{ padding: '16px 18px 32px', display: 'flex', flexDirection: 'column', gap: 14 }}>

        <Card theme={theme}>
          <SectionLabel theme={theme}>rhizome reports</SectionLabel>
          <div style={{ fontFamily: POLLEN_FONT_MONO, fontSize: 13, color: theme.humus, lineHeight: 1.6 }}>
            soil_a: <strong>31%</strong> · soil_b: <strong>28%</strong>
            <br/>tank: <strong>30%</strong>
            <br/>last_water: <strong>08:42 · 12s</strong>
          </div>
        </Card>

        <Card theme={theme} padding={0}>
          <div style={{ padding: '14px 16px', borderBottom: `1px solid ${theme.borderSubtle}` }}>
            <SectionLabel theme={theme}>{copy.auditPlaceholder}</SectionLabel>
          </div>
          <textarea
            value={obs}
            onChange={e => { setObs(e.target.value); setResult(null); }}
            placeholder={lang === 'es' ? "El sustrato parece seco al tacto…" : "The soil looks dry to the touch…"}
            style={{
              width: '100%', minHeight: 80, border: 'none', resize: 'none', padding: 16,
              fontFamily: POLLEN_FONT_SANS, fontSize: 14, color: theme.humus,
              background: 'transparent', outline: 'none', boxSizing: 'border-box',
            }}
          />
          <div style={{ padding: 12, display: 'flex', gap: 8, borderTop: `1px solid ${theme.borderSubtle}` }}>
            <PrimaryButton theme={theme} kind="secondary" onClick={() => submit('match')} full={false}>
              {lang === 'es' ? 'Coincide' : 'Matches'}
            </PrimaryButton>
            <PrimaryButton theme={theme} kind="primary" onClick={() => submit('conflict')}>
              {lang === 'es' ? 'No coincide' : 'Disagrees'}
            </PrimaryButton>
          </div>
        </Card>

        {result === 'match' && (
          <JurisdictionBanner kind="ai" theme={theme}>{copy.auditMatch}</JurisdictionBanner>
        )}
        {result === 'conflict' && (
          <>
            <JurisdictionBanner kind="warning" theme={theme}>{copy.auditConflict}</JurisdictionBanner>
            <Card theme={theme}>
              <SectionLabel theme={theme}>dispute · ledger entry</SectionLabel>
              <div style={{ fontFamily: POLLEN_FONT_MONO, fontSize: 12, color: theme.humus, lineHeight: 1.6 }}>
                human_note: <em style={{ color: theme.moss }}>{obs || (lang==='es'?'sustrato visiblemente seco':'soil looks visibly dry')}</em>
                <br/>rhizome_reading: soil_a <strong>31%</strong>
                <br/>resolution: <span style={{ color: theme.warn }}>third_reading_requested</span>
                <br/>ttl: 6h
              </div>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}

// ───────────────────────────────────────────────
// CONTEXT FERRY
// ───────────────────────────────────────────────
function FerryScreen({ theme, copy, lang, onBack }) {
  const [state, setState] = useState2('ready'); // ready | delivered | expired
  return (
    <div style={{ background: theme.bg, minHeight: '100%' }}>
      <ScreenHeader title={copy.carryContext} subtitle="ferry.bundle · WeatherDigest" theme={theme} onBack={onBack} />
      <div style={{ padding: '16px 18px 32px', display: 'flex', flexDirection: 'column', gap: 14 }}>

        <Card theme={theme} accent={state === 'expired' ? theme.blocked : theme.water}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
            <MonoID theme={theme} size={13}>WeatherDigest</MonoID>
            {state === 'ready' && <StatusChip kind="water" label={lang==='es'?'LISTO':'READY'} theme={theme} mono />}
            {state === 'delivered' && <StatusChip kind="validated" label={copy.ackReceived} theme={theme} mono />}
            {state === 'expired' && <StatusChip kind="expired" label={copy.expired} theme={theme} mono />}
          </div>
          <div style={{ fontFamily: POLLEN_FONT_MONO, fontSize: 12, color: theme.humus, lineHeight: 1.7 }}>
            source: <strong>RHIZOME_01</strong>
            <br/>contains: forecast · alerts · visit_notes
            <br/>valid_until: <strong>18:00</strong> {state === 'expired' && <span style={{ color: theme.blocked }}>· EXPIRED</span>}
            <br/>size: 1.4 KB
          </div>
        </Card>

        {state === 'ready' && <JurisdictionBanner kind="info" theme={theme}>{copy.contextReady}</JurisdictionBanner>}
        {state === 'delivered' && <JurisdictionBanner kind="ai" theme={theme}>{copy.contextDelivered}</JurisdictionBanner>}
        {state === 'expired' && <JurisdictionBanner kind="blocked" theme={theme}>{copy.contextExpired}</JurisdictionBanner>}

        <SectionLabel theme={theme}>{lang==='es'?'rhizomes a entregar':'deliverable rhizomes'}</SectionLabel>
        <Card theme={theme}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <MonoID theme={theme}>RHIZOME_02</MonoID>
              <div style={{ fontFamily: POLLEN_FONT_SANS, fontSize: 12, color: theme.humusDim, marginTop: 2 }}>PLOT_02 · stale 3h</div>
            </div>
            {state === 'ready' && (
              <PrimaryButton theme={theme} kind="primary" full={false} size="md" onClick={() => setState('delivered')}>
                {copy.deliverToRhizome}
              </PrimaryButton>
            )}
          </div>
        </Card>

        {state === 'delivered' && (
          <PrimaryButton theme={theme} kind="ghost" onClick={() => setState('ready')}>
            ↺ {lang==='es'?'Cargar otro bundle':'Load another bundle'}
          </PrimaryButton>
        )}
        {state === 'ready' && (
          <PrimaryButton theme={theme} kind="ghost" onClick={() => setState('expired')}>
            {lang==='es'?'simular caducidad':'simulate expiry'}
          </PrimaryButton>
        )}
      </div>
    </div>
  );
}

// ───────────────────────────────────────────────
// LEDGER
// ───────────────────────────────────────────────
function LedgerScreen({ theme, copy, lang, onBack, density = 'cards' }) {
  const [filter, setFilter] = useState2('all');
  const filters = [
    { id: 'all', label: lang==='es'?'TODO':'ALL' },
    { id: 'water', label: copy.receiptWater },
    { id: 'skip', label: copy.receiptSkip },
    { id: 'blocked', label: copy.receiptBlocked },
    { id: 'updated', label: copy.receiptUpdated },
    { id: 'expired', label: copy.receiptExpired },
  ];
  const items = MOCK_RECEIPTS_KEYS.filter(r => filter === 'all' || r.kind === filter);

  return (
    <div style={{ background: theme.bg, minHeight: '100%' }}>
      <ScreenHeader title={copy.viewLog} subtitle="water ledger · PLOT_01" theme={theme} onBack={onBack} />
      <div style={{ padding: '16px 18px 32px', display: 'flex', flexDirection: 'column', gap: 14 }}>

        {/* Active policy */}
        <Card theme={theme}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
            <SectionLabel theme={theme}>{copy.activePolicy}</SectionLabel>
            <StatusChip kind="validated" label="ACK" theme={theme} mono />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', rowGap: 4, columnGap: 12,
              fontFamily: POLLEN_FONT_MONO, fontSize: 12, color: theme.humus }}>
            <span style={{ color: theme.humusDim }}>{copy.budgetCap}</span><span>900</span>
            <span style={{ color: theme.humusDim }}>{copy.wateringWindow}</span><span>06:00–10:00</span>
            <span style={{ color: theme.humusDim }}>{copy.mode}</span><span>{copy.survival}</span>
          </div>
          <div style={{ marginTop: 14 }}>
            <LedgerBar used={240} blocked={0} remaining={660} total={900} theme={theme} />
          </div>
        </Card>

        {/* Filter chips */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {filters.map(f => (
            <button key={f.id} onClick={() => setFilter(f.id)} style={{
              padding: '6px 10px', borderRadius: 100,
              border: `1px solid ${filter === f.id ? theme.humus : theme.border}`,
              background: filter === f.id ? theme.humus : 'transparent',
              color: filter === f.id ? theme.bg : theme.humus,
              fontFamily: POLLEN_FONT_MONO, fontSize: 10.5, fontWeight: 600, letterSpacing: 0.5,
              cursor: 'pointer',
            }}>{f.label}</button>
          ))}
        </div>

        {/* Receipts */}
        {density === 'compact' ? (
          <Card theme={theme} padding={0}>
            {items.map((r, i) => (
              <div key={i} style={{
                padding: '10px 14px',
                borderBottom: i < items.length-1 ? `1px solid ${theme.borderSubtle}` : 'none',
                display: 'grid', gridTemplateColumns: '90px 1fr auto', gap: 10, alignItems: 'center',
                fontFamily: POLLEN_FONT_MONO, fontSize: 11.5,
              }}>
                <span style={{ color: r.kind === 'water' ? theme.water : r.kind === 'blocked' || r.kind === 'expired' ? theme.blocked : theme.humusDim, fontWeight: 600 }}>
                  {RECEIPT_LABEL(r.kind, copy)}{r.s ? ` ${r.s}s` : ''}
                </span>
                <span style={{ color: theme.humusDim }}>
                  {r.soil != null ? `soil ${r.soil}% · thr ${r.threshold}%` : RECEIPT_REASON_TXT(r.reason, lang).split('.')[0]}
                </span>
                <span style={{ color: theme.humusDim }}>{r.time}</span>
              </div>
            ))}
          </Card>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {items.map((r, i) => (
              <ReceiptCard key={i}
                kind={RECEIPT_LABEL(r.kind, copy)}
                durationS={r.s} timestamp={r.time} plot={r.plot}
                evidence={r.soil != null ? `soil ${r.soil}% · threshold ${r.threshold}%${r.budget != null ? ` · budget left ${r.budget} ml` : ''}` : null}
                reason={RECEIPT_REASON_TXT(r.reason, lang)}
                theme={theme} copy={copy}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ───────────────────────────────────────────────
// MERISTEM SYNC
// ───────────────────────────────────────────────
function MeristemSyncScreen({ theme, copy, lang, onBack }) {
  const [step, setStep] = useState2(0);
  const steps = [
    { label: copy.pullData,        sub: 'RHIZOME_01 · 6.2 KB' },
    { label: copy.uploadBundle,    sub: 'wifi · 802.11n' },
    { label: copy.downloadPolicy,  sub: 'PolicyPacket v0.4' },
    { label: copy.confirmPolicy,   sub: 'awaiting human review' },
  ];

  const advance = () => setStep(s => Math.min(s+1, steps.length));

  return (
    <div style={{ background: theme.bg, minHeight: '100%' }}>
      <ScreenHeader title={copy.meristemSync} subtitle={copy.meristemSub} theme={theme} onBack={onBack} />
      <div style={{ padding: '16px 18px 32px', display: 'flex', flexDirection: 'column', gap: 14 }}>

        <Card theme={theme} padding={0}>
          <div style={{ padding: '14px 14px 4px' }}>
            <SectionLabel theme={theme}>handoff</SectionLabel>
          </div>
          <div style={{ padding: '0 14px 12px' }}>
            {steps.map((s, i) => (
              <SyncStep key={i} label={s.label} sub={i < step ? s.sub : i === step ? s.sub : ''}
                status={i < step ? 'done' : i === step ? 'active' : 'pending'} theme={theme} />
            ))}
          </div>
        </Card>

        {step >= steps.length && (
          <JurisdictionBanner kind="ai" theme={theme}>{copy.policyDownloaded}</JurisdictionBanner>
        )}

        <PrimaryButton theme={theme} kind={step >= steps.length ? 'ai' : 'primary'}
          onClick={step >= steps.length ? onBack : advance}>
          {step >= steps.length ? (lang==='es'?'Aplicar a Rhizome':'Apply to Rhizome') : (lang==='es'?'Continuar':'Continue')} →
        </PrimaryButton>

        {/* Technical panel */}
        <details style={{
          background: theme.graphite, color: theme.bg, borderRadius: 10, padding: '12px 14px',
          fontFamily: POLLEN_FONT_MONO, fontSize: 11.5,
        }}>
          <summary style={{ cursor: 'pointer', color: theme.seed, letterSpacing: 0.5 }}>
            {copy.modelTelemetry.toLowerCase()}
          </summary>
          <div style={{ marginTop: 10, lineHeight: 1.7, color: '#dfd8cc' }}>
            <div style={{ color: theme.seed }}>{copy.onDevice}</div>
            <div style={{ marginTop: 6 }}>TTFT &nbsp; 420 ms</div>
            <div>ms/token &nbsp; 38</div>
            <div>context_budget &nbsp; 4096</div>
            <div>thinking &nbsp; off</div>
          </div>
        </details>
      </div>
    </div>
  );
}

// ───────────────────────────────────────────────
// ACK toast (reusable)
// ───────────────────────────────────────────────
function AckToast({ theme, copy, visible }) {
  if (!visible) return null;
  return (
    <div style={{
      position: 'absolute', left: 16, right: 16, bottom: 28, zIndex: 10,
      background: theme.humus, color: theme.bg,
      padding: '14px 16px', borderRadius: 12,
      border: `1px solid ${theme.humus}`,
      display: 'flex', alignItems: 'center', gap: 12,
      fontFamily: POLLEN_FONT_SANS, fontSize: 13.5,
      boxShadow: '0 8px 24px rgba(0,0,0,0.18)',
      animation: 'pollenSlideUp 280ms ease-out',
    }}>
      <Dot color={theme.seed} size={8} />
      <span style={{ flex: 1 }}>{copy.visitComplete.split('\n')[0]}</span>
      <MonoID theme={{ humus: theme.bg }} size={11} color={theme.seed}>ACK</MonoID>
    </div>
  );
}

Object.assign(window, {
  MissionCompilerScreen, AskScreen, AuditScreen, FerryScreen,
  LedgerScreen, MeristemSyncScreen, AckToast,
});
