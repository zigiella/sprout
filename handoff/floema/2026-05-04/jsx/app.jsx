// Pollen — main app: routing, theme, tweaks

const { useState: useS, useEffect: useE } = React;

const ROUTES = {
  HOME: 'home',
  RHIZOME: 'rhizome',
  VISIT: 'visit',
  MISSION: 'mission',
  ASK: 'ask',
  AUDIT: 'audit',
  FERRY: 'ferry',
  LEDGER: 'ledger',
  SYNC: 'sync',
};

const POLLEN_TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "language": "en",
  "outdoorMode": false,
  "homeLayout": "card",
  "missionVariant": "voice",
  "ledgerDensity": "cards",
  "showFrame": true
}/*EDITMODE-END*/;

function PollenApp() {
  const [tweaks, setTweak] = useTweaks(POLLEN_TWEAK_DEFAULTS);
  const lang = tweaks.language;
  const copy = window.POLLEN_COPY[lang];
  const theme = tweaks.outdoorMode ? POLLEN_TOKENS.outdoor : POLLEN_TOKENS.light;

  const [route, setRoute] = useS(ROUTES.HOME);
  const [activeRhizome, setActiveRhizome] = useS(null);
  const [stack, setStack] = useS([ROUTES.HOME]);
  const [showAck, setShowAck] = useS(false);

  const go = (next, payload) => {
    if (next === ROUTES.RHIZOME && payload) setActiveRhizome(payload);
    setRoute(next);
    setStack(s => [...s, next]);
  };
  const back = () => {
    setStack(s => {
      const ns = s.slice(0, -1);
      const r = ns[ns.length - 1] || ROUTES.HOME;
      setRoute(r);
      return ns.length ? ns : [ROUTES.HOME];
    });
  };

  const onLangToggle = () => setTweak('language', lang === 'en' ? 'es' : 'en');

  const screen = (() => {
    switch (route) {
      case ROUTES.HOME:
        return <HomeScreen theme={theme} copy={copy} lang={lang}
          onLangToggle={onLangToggle}
          onOpenRhizome={r => go(ROUTES.RHIZOME, r)}
          onOpenSync={() => go(ROUTES.SYNC)}
          layout={tweaks.homeLayout}
        />;
      case ROUTES.RHIZOME:
        return <RhizomeStatusScreen theme={theme} copy={copy} lang={lang}
          onBack={back} rhizome={activeRhizome || MOCK_RHIZOMES[0]}
          onAction={a => {
            if (a === 'visit') go(ROUTES.VISIT);
            else if (a === 'ask') go(ROUTES.ASK);
            else if (a === 'mission') go(ROUTES.MISSION);
            else if (a === 'audit') go(ROUTES.AUDIT);
            else if (a === 'ferry') go(ROUTES.FERRY);
            else if (a === 'ledger') go(ROUTES.LEDGER);
          }}
        />;
      case ROUTES.VISIT:
        return <VisitConsoleScreen theme={theme} copy={copy} lang={lang}
          onBack={back} rhizome={activeRhizome || MOCK_RHIZOMES[0]}
          onSubScreen={a => {
            if (a === 'ask') go(ROUTES.ASK);
            else if (a === 'mission') go(ROUTES.MISSION);
            else if (a === 'audit') go(ROUTES.AUDIT);
            else if (a === 'ferry') go(ROUTES.FERRY);
          }}
        />;
      case ROUTES.MISSION:
        return <MissionCompilerScreen theme={theme} copy={copy} lang={lang}
          onBack={back} variant={tweaks.missionVariant}
          onAck={() => {
            setShowAck(true);
            setTimeout(() => { setShowAck(false); back(); }, 1800);
          }}
        />;
      case ROUTES.ASK:
        return <AskScreen theme={theme} copy={copy} lang={lang} onBack={back} />;
      case ROUTES.AUDIT:
        return <AuditScreen theme={theme} copy={copy} lang={lang} onBack={back} />;
      case ROUTES.FERRY:
        return <FerryScreen theme={theme} copy={copy} lang={lang} onBack={back} />;
      case ROUTES.LEDGER:
        return <LedgerScreen theme={theme} copy={copy} lang={lang} onBack={back} density={tweaks.ledgerDensity} />;
      case ROUTES.SYNC:
        return <MeristemSyncScreen theme={theme} copy={copy} lang={lang} onBack={back} />;
      default:
        return null;
    }
  })();

  // Bottom nav
  const navItems = [
    { id: ROUTES.HOME, label: copy.home, glyph: '⌂' },
    { id: ROUTES.RHIZOME, label: copy.visit, glyph: '◉' },
    { id: ROUTES.LEDGER, label: copy.ledger, glyph: '≡' },
    { id: ROUTES.SYNC, label: copy.sync, glyph: '◇' },
  ];

  const navigate = id => {
    if (id === ROUTES.RHIZOME) {
      setActiveRhizome(MOCK_RHIZOMES[0]);
    }
    setRoute(id);
    setStack([ROUTES.HOME, ...(id === ROUTES.HOME ? [] : [id])]);
  };

  const navBar = (
    <div data-screen-label="bottom-nav" style={{
      display: 'flex', borderTop: `1px solid ${theme.borderSubtle}`,
      background: theme.bg,
    }}>
      {navItems.map(n => {
        const active = route === n.id || (n.id === ROUTES.RHIZOME && [ROUTES.RHIZOME, ROUTES.VISIT, ROUTES.MISSION, ROUTES.ASK, ROUTES.AUDIT, ROUTES.FERRY].includes(route));
        return (
          <button key={n.id} onClick={() => navigate(n.id)} style={{
            flex: 1, padding: '10px 4px 12px',
            background: 'transparent', border: 'none', cursor: 'pointer',
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2,
            color: active ? theme.humus : theme.humusDim,
            borderTop: active ? `2px solid ${theme.humus}` : '2px solid transparent',
          }}>
            <span style={{ fontFamily: POLLEN_FONT_MONO, fontSize: 16 }}>{n.glyph}</span>
            <span style={{ fontFamily: POLLEN_FONT_SANS, fontSize: 10.5, fontWeight: 600, letterSpacing: 0.3 }}>{n.label}</span>
          </button>
        );
      })}
    </div>
  );

  const appContent = (
    <div data-screen-label={`pollen-${route}`} style={{
      width: '100%', height: '100%', position: 'relative',
      display: 'flex', flexDirection: 'column',
      background: theme.bg, color: theme.humus,
    }}>
      <div style={{ flex: 1, overflow: 'auto', position: 'relative' }}>
        {screen}
        <AckToast theme={theme} copy={copy} visible={showAck} />
      </div>
      {navBar}
    </div>
  );

  // ─── Tweaks panel ───
  const tweaksUI = (
    <TweaksPanel title="Pollen tweaks">
      <TweakSection title="Display">
        <TweakRadio
          label="Language"
          value={lang}
          options={[{ value: 'en', label: 'EN' }, { value: 'es', label: 'ES' }]}
          onChange={v => setTweak('language', v)}
        />
        <TweakToggle label="Outdoor mode (high-contrast)"
          value={tweaks.outdoorMode}
          onChange={v => setTweak('outdoorMode', v)} />
        <TweakToggle label="Show Android frame"
          value={tweaks.showFrame}
          onChange={v => setTweak('showFrame', v)} />
      </TweakSection>
      <TweakSection title="Variations">
        <TweakRadio
          label="Home layout"
          value={tweaks.homeLayout}
          options={[{ value: 'card', label: 'Card' }, { value: 'compact', label: 'Compact' }]}
          onChange={v => setTweak('homeLayout', v)}
        />
        <TweakRadio
          label="Mission compiler"
          value={tweaks.missionVariant}
          options={[{ value: 'voice', label: 'Voice' }, { value: 'text', label: 'Text' }]}
          onChange={v => setTweak('missionVariant', v)}
        />
        <TweakRadio
          label="Ledger density"
          value={tweaks.ledgerDensity}
          options={[{ value: 'cards', label: 'Cards' }, { value: 'compact', label: 'Compact' }]}
          onChange={v => setTweak('ledgerDensity', v)}
        />
      </TweakSection>
    </TweaksPanel>
  );

  return (
    <div style={{
      minHeight: '100vh',
      background: '#1f1d1a',
      backgroundImage: 'radial-gradient(circle at 50% 20%, #2a2724 0%, #16140f 80%)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '24px 16px',
      fontFamily: POLLEN_FONT_SANS,
    }}>
      {tweaks.showFrame ? (
        <AndroidDevice width={412} height={892}>
          {appContent}
        </AndroidDevice>
      ) : (
        <div style={{
          width: 412, height: 892, borderRadius: 18, overflow: 'hidden',
          boxShadow: '0 30px 80px rgba(0,0,0,0.35)',
        }}>{appContent}</div>
      )}
      {tweaksUI}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<PollenApp />);
