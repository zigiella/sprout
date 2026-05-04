// Pollen — design tokens (Soil protocol + Water ledger)
// Two themes: light (soil.oat warm) and outdoor high-contrast (max legibility)

const POLLEN_TOKENS = {
  light: {
    // Soil
    bg: '#F3EDE4',          // soil.oat
    surface: '#FAF6EF',     // surface tint
    surfaceAlt: '#EDE4D6',  // soil between oat and ash
    ash: '#D8CBBE',         // soil.ash — dividers
    kraft: '#C9A97E',       // soil.kraft — material accent
    clay: '#8A654B',        // soil.clay — physical accent
    clayDim: '#A88670',
    moss: '#667554',        // soil.moss — vegetal sober
    mossDim: '#8A9874',
    humus: '#2A221D',       // soil.humus — text
    humusDim: '#4B4540',
    graphite: '#1A1A18',    // for terminal blocks

    // Water ledger
    water: '#3B82F6',
    waterDeep: '#1D4ED8',
    waterTint: '#DCEBFF',

    // Status
    ok: '#4F8A5B',
    warn: '#F59E0B',
    blocked: '#B94A3D',
    blockedTint: '#F6D6D1',
    seed: '#C5F26B',        // signal.seed — AI active

    // Borders
    border: '#CDBBAA',
    borderStrong: '#8A654B',
    borderSubtle: '#E0D4C5',
  },
  outdoor: {
    bg: '#FFF8EA',
    surface: '#FFFFFF',
    surfaceAlt: '#EFE2CD',
    ash: '#D8CBBE',
    kraft: '#C9A97E',
    clay: '#5E4A38',
    clayDim: '#7A5E48',
    moss: '#3E5234',
    mossDim: '#5E7148',
    humus: '#000000',
    humusDim: '#1A1A18',
    graphite: '#000000',

    water: '#005BBB',
    waterDeep: '#003D80',
    waterTint: '#DCEBFF',

    ok: '#0F6B2F',
    warn: '#9B6B00',
    blocked: '#9B1C1C',
    blockedTint: '#FFDAD6',
    seed: '#6B9F00',

    border: '#000000',
    borderStrong: '#000000',
    borderSubtle: '#5E5348',
  }
};

// Type stack
const POLLEN_FONT_SANS = "'Manrope', -apple-system, BlinkMacSystemFont, sans-serif";
const POLLEN_FONT_MONO = "'IBM Plex Mono', ui-monospace, 'SF Mono', Menlo, monospace";

// ───────────────────────────────────────────────
// Reusable atoms
// ───────────────────────────────────────────────

function StatusChip({ kind = 'connected', label, theme, mono = false, subtle = false }) {
  const t = theme;
  const palette = {
    connected: { bg: t.ok + '22', fg: t.ok, border: t.ok },
    offline:   { bg: t.clay + '20', fg: t.clay, border: t.clay },
    stale:     { bg: t.warn + '22', fg: '#8a5a05', border: t.warn },
    error:     { bg: t.blocked + '22', fg: t.blocked, border: t.blocked },
    syncing:   { bg: t.seed + '40', fg: '#3a5610', border: t.moss },
    ai:        { bg: t.seed + '50', fg: '#3a5610', border: '#9bbe3e' },
    blocked:   { bg: t.blockedTint, fg: t.blocked, border: t.blocked },
    expired:   { bg: t.blockedTint, fg: t.blocked, border: t.blocked },
    validated: { bg: t.ok + '22', fg: t.ok, border: t.ok },
    neutral:   { bg: 'transparent', fg: t.humusDim, border: t.border },
    water:     { bg: t.waterTint, fg: t.waterDeep, border: t.water },
  };
  const p = palette[kind] || palette.neutral;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '4px 8px', borderRadius: 4,
      fontFamily: mono ? POLLEN_FONT_MONO : POLLEN_FONT_SANS,
      fontSize: 11, fontWeight: 600, letterSpacing: 0.6,
      textTransform: 'uppercase',
      color: p.fg,
      background: subtle ? 'transparent' : p.bg,
      border: `1px solid ${p.border}`,
      lineHeight: '14px',
      whiteSpace: 'nowrap',
    }}>
      {kind === 'ai' && <SeedPulse color={p.fg} />}
      {kind === 'connected' && <Dot color={p.fg} />}
      {label}
    </span>
  );
}

function Dot({ color, size = 6 }) {
  return <span style={{
    width: size, height: size, borderRadius: '50%', background: color, display: 'inline-block'
  }} />;
}

function SeedPulse({ color = '#9bbe3e' }) {
  return (
    <span style={{ position: 'relative', width: 8, height: 8, display: 'inline-block' }}>
      <span style={{
        position: 'absolute', inset: 0, borderRadius: '50%',
        background: color, animation: 'pollenPulse 1.6s ease-out infinite',
      }} />
      <span style={{
        position: 'absolute', inset: 2, borderRadius: '50%', background: color,
      }} />
    </span>
  );
}

// Section label — small uppercase mono
function SectionLabel({ children, theme, color }) {
  return (
    <div style={{
      fontFamily: POLLEN_FONT_MONO,
      fontSize: 11, fontWeight: 500, letterSpacing: 0.6,
      textTransform: 'uppercase',
      color: color || theme.humusDim,
      marginBottom: 8,
    }}>{children}</div>
  );
}

// Card
function Card({ children, theme, padding = 16, accent, blocked, style = {} }) {
  return (
    <div style={{
      background: theme.surface,
      border: `1px solid ${blocked ? theme.blocked : theme.border}`,
      borderLeft: accent ? `3px solid ${accent}` : (blocked ? `2px double ${theme.blocked}` : `1px solid ${blocked ? theme.blocked : theme.border}`),
      borderRadius: 12,
      padding,
      ...style,
    }}>
      {children}
    </div>
  );
}

// Telemetry tile (Tank / Soil / Flow)
function TelemetryTile({ label, value, unit, sub, bar, theme, color, danger }) {
  const c = danger ? theme.blocked : (color || theme.humus);
  return (
    <div style={{
      flex: 1, minWidth: 0,
      background: theme.surface,
      border: `1px solid ${theme.border}`,
      borderRadius: 12,
      padding: 14,
      display: 'flex', flexDirection: 'column', gap: 6,
    }}>
      <div style={{
        fontFamily: POLLEN_FONT_MONO, fontSize: 10, fontWeight: 500, letterSpacing: 0.6,
        color: theme.humusDim, textTransform: 'uppercase',
      }}>{label}</div>
      <div style={{
        display: 'flex', alignItems: 'baseline', gap: 4,
      }}>
        <span style={{
          fontFamily: POLLEN_FONT_SANS, fontSize: 28, fontWeight: 700, color: c,
          lineHeight: 1, letterSpacing: -0.5,
        }}>{value}</span>
        {unit && <span style={{
          fontFamily: POLLEN_FONT_MONO, fontSize: 12, color: theme.humusDim,
        }}>{unit}</span>}
      </div>
      {bar !== undefined && (
        <div style={{
          height: 4, background: theme.surfaceAlt, borderRadius: 2, overflow: 'hidden',
          marginTop: 2,
        }}>
          <div style={{
            height: '100%', width: `${Math.max(2, Math.min(100, bar))}%`,
            background: c, borderRadius: 2,
            transition: 'width 600ms ease',
          }} />
        </div>
      )}
      {sub && <div style={{
        fontFamily: POLLEN_FONT_MONO, fontSize: 11, color: theme.humusDim,
      }}>{sub}</div>}
    </div>
  );
}

// Primary action button
function PrimaryButton({ children, onClick, theme, kind = 'primary', disabled, loading, icon, full = true, size = 'lg' }) {
  const palettes = {
    primary: { bg: theme.humus, fg: theme.bg, border: theme.humus },
    secondary: { bg: 'transparent', fg: theme.humus, border: theme.borderStrong },
    water: { bg: theme.water, fg: '#fff', border: theme.water },
    ai: { bg: theme.seed, fg: theme.humus, border: '#9bbe3e' },
    danger: { bg: theme.blocked, fg: '#fff', border: theme.blocked },
    ghost: { bg: 'transparent', fg: theme.humus, border: 'transparent' },
  };
  const p = palettes[kind];
  const heights = { lg: 48, md: 40, sm: 32 };
  return (
    <button
      onClick={disabled || loading ? undefined : onClick}
      disabled={disabled}
      style={{
        height: heights[size],
        width: full ? '100%' : 'auto',
        padding: '0 20px',
        background: p.bg, color: p.fg,
        border: `1px solid ${p.border}`,
        borderRadius: 14,
        fontFamily: POLLEN_FONT_SANS,
        fontSize: 15, fontWeight: 650, letterSpacing: 0.1,
        display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8,
        cursor: disabled || loading ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        transition: 'transform 80ms ease',
        WebkitTapHighlightColor: 'transparent',
      }}
      onMouseDown={e => { if (!disabled && !loading) e.currentTarget.style.transform = 'scale(0.98)'; }}
      onMouseUp={e => e.currentTarget.style.transform = ''}
      onMouseLeave={e => e.currentTarget.style.transform = ''}
    >
      {loading ? <span style={{ fontFamily: POLLEN_FONT_MONO, fontSize: 13 }}>· · ·</span> : icon}
      {children}
    </button>
  );
}

// Receipt card
function ReceiptCard({ kind = 'WATER', timestamp, plot, evidence, reason, durationS, theme, copy }) {
  const kindColors = {
    WATER: theme.water, RIEGO: theme.water,
    SKIP: theme.humusDim, OMITIDO: theme.humusDim,
    DEFER: theme.warn, ESPERA: theme.warn,
    BLOCKED: theme.blocked, BLOQUEADO: theme.blocked,
    UPDATED: theme.moss, ACTUALIZADO: theme.moss,
    EXPIRED: theme.blocked, CADUCADO: theme.blocked,
  };
  const c = kindColors[kind] || theme.humus;
  const isBlocked = kind === 'BLOCKED' || kind === 'BLOQUEADO' || kind === 'EXPIRED' || kind === 'CADUCADO';
  return (
    <div style={{
      background: theme.surface,
      border: `1px solid ${theme.border}`,
      borderLeft: `3px solid ${c}`,
      borderRadius: 8,
      padding: '12px 14px',
      display: 'flex', flexDirection: 'column', gap: 6,
      ...(isBlocked ? { borderTop: `1px double ${theme.blocked}`, borderBottom: `1px double ${theme.blocked}` } : {})
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 8 }}>
        <span style={{
          fontFamily: POLLEN_FONT_MONO, fontSize: 12, fontWeight: 600, color: c, letterSpacing: 0.5,
        }}>{kind}{durationS ? ` · ${durationS}s` : ''}</span>
        <span style={{
          fontFamily: POLLEN_FONT_MONO, fontSize: 11, color: theme.humusDim,
        }}>{timestamp}{plot ? ` · ${plot}` : ''}</span>
      </div>
      {evidence && <div style={{
        fontFamily: POLLEN_FONT_MONO, fontSize: 11.5, color: theme.humus, lineHeight: 1.5,
      }}>{evidence}</div>}
      {reason && <div style={{
        fontFamily: POLLEN_FONT_SANS, fontSize: 13, color: theme.humusDim, lineHeight: 1.4,
      }}>{reason}</div>}
    </div>
  );
}

// Mono ID label
function MonoID({ children, theme, color, size = 12, weight = 600 }) {
  return (
    <span style={{
      fontFamily: POLLEN_FONT_MONO, fontSize: size, fontWeight: weight,
      color: color || theme.humus, letterSpacing: 0.4,
    }}>{children}</span>
  );
}

// Sync step
function SyncStep({ label, status, sub, theme }) {
  const statusColors = {
    pending: { dot: theme.ash, text: theme.humusDim },
    active:  { dot: theme.seed, text: theme.humus },
    done:    { dot: theme.ok, text: theme.humus },
    warning: { dot: theme.warn, text: theme.humus },
    failed:  { dot: theme.blocked, text: theme.humus },
  };
  const sc = statusColors[status] || statusColors.pending;
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', gap: 12,
      padding: '10px 0',
      borderBottom: `1px solid ${theme.borderSubtle}`,
    }}>
      <div style={{
        width: 18, height: 18, borderRadius: 4,
        marginTop: 2,
        border: `1px solid ${status === 'pending' ? theme.border : sc.dot}`,
        background: status === 'done' || status === 'active' || status === 'warning' ? sc.dot : 'transparent',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0,
        position: 'relative',
      }}>
        {status === 'done' && (
          <svg width="10" height="10" viewBox="0 0 10 10"><path d="M2 5l2 2 4-4" stroke="#fff" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round"/></svg>
        )}
        {status === 'active' && <SeedPulse color={theme.moss} />}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontFamily: POLLEN_FONT_SANS, fontSize: 14, fontWeight: 500, color: sc.text,
        }}>{label}</div>
        {sub && <div style={{
          fontFamily: POLLEN_FONT_MONO, fontSize: 11, color: theme.humusDim, marginTop: 2,
        }}>{sub}</div>}
      </div>
    </div>
  );
}

// Jurisdiction banner
function JurisdictionBanner({ kind = 'info', children, theme }) {
  const palettes = {
    info: { bg: theme.surfaceAlt, border: theme.border, fg: theme.humus, glyph: 'i' },
    warning: { bg: theme.warn + '15', border: theme.warn, fg: '#8a5a05', glyph: '!' },
    blocked: { bg: theme.blockedTint, border: theme.blocked, fg: theme.blocked, glyph: '×' },
    physical: { bg: theme.surfaceAlt, border: theme.clay, fg: theme.humus, glyph: '⏚' },
    ai: { bg: theme.seed + '30', border: theme.moss, fg: '#3a5610', glyph: '◇' },
  };
  const p = palettes[kind];
  const isBlocked = kind === 'blocked';
  return (
    <div style={{
      background: p.bg,
      border: `1px solid ${p.border}`,
      ...(isBlocked ? { borderWidth: '1px', boxShadow: `inset 0 0 0 1px ${p.border}, 0 0 0 1px ${p.border}` } : {}),
      borderRadius: 8,
      padding: '12px 14px',
      display: 'flex', gap: 12, alignItems: 'flex-start',
    }}>
      <div style={{
        width: 22, height: 22, borderRadius: 4,
        border: `1px solid ${p.border}`, color: p.fg,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: POLLEN_FONT_MONO, fontSize: 13, fontWeight: 600,
        flexShrink: 0,
      }}>{p.glyph}</div>
      <div style={{
        flex: 1,
        fontFamily: POLLEN_FONT_SANS, fontSize: 13.5, lineHeight: 1.45,
        color: p.fg, whiteSpace: 'pre-line',
      }}>{children}</div>
    </div>
  );
}

// Ledger bar
function LedgerBar({ used, blocked, remaining, total, theme }) {
  const u = used / total * 100;
  const b = blocked / total * 100;
  return (
    <div>
      <div style={{
        height: 14, background: theme.surfaceAlt, borderRadius: 4, overflow: 'hidden',
        display: 'flex', border: `1px solid ${theme.border}`,
      }}>
        <div style={{ width: `${u}%`, background: theme.water, height: '100%' }} />
        <div style={{ width: `${b}%`, background: theme.blocked, height: '100%' }} />
      </div>
      <div style={{
        display: 'flex', justifyContent: 'space-between', marginTop: 6,
        fontFamily: POLLEN_FONT_MONO, fontSize: 11, color: theme.humusDim,
      }}>
        <span>{used} ml used</span>
        {blocked > 0 && <span style={{ color: theme.blocked }}>{blocked} ml blocked</span>}
        <span>{remaining} ml left · {total} ml cap</span>
      </div>
    </div>
  );
}

Object.assign(window, {
  POLLEN_TOKENS, POLLEN_FONT_SANS, POLLEN_FONT_MONO,
  StatusChip, Dot, SeedPulse, SectionLabel, Card, TelemetryTile,
  PrimaryButton, ReceiptCard, MonoID, SyncStep, JurisdictionBanner, LedgerBar,
});
