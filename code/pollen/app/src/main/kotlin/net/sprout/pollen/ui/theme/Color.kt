// Sprout · Pollen — Material 3 color schemes
// Generated from design tokens. Three schemes: light, dark, outdoor.
// Outdoor is high-contrast (NOT just dark). Use a custom CompositionLocal
// or your own ThemeMode enum to switch — Material 3 only ships light/dark.

package net.sprout.pollen.ui.theme

import androidx.compose.material3.ColorScheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

// ───────── Brand tokens (raw) ─────────
object SproutColors {
    // Soil
    val Oat       = Color(0xFFF3EDE4)
    val Surface   = Color(0xFFFAF6EF)
    val Ash       = Color(0xFFD8CBBE)
    val Kraft     = Color(0xFFC9A97E)
    val Clay      = Color(0xFF8A654B)
    val Moss      = Color(0xFF667554)
    val Humus     = Color(0xFF2A221D)
    val Graphite  = Color(0xFF1A1A18)

    // Water ledger
    val Water       = Color(0xFF3B82F6)
    val WaterDeep   = Color(0xFF1D4ED8)
    val WaterTint   = Color(0xFFDCEBFF)

    // Status
    val Ok          = Color(0xFF4F8A5B)
    val Warn        = Color(0xFFF59E0B)
    val Blocked     = Color(0xFFB94A3D)
    val BlockedTint = Color(0xFFF6D6D1)

    // Signal
    val Seed        = Color(0xFFC5F26B)   // AI active — pulse only

    // Borders
    val Border       = Color(0xFFCDBBAA)
    val BorderStrong = Color(0xFF8A654B)
    val BorderSubtle = Color(0xFFE0D4C5)

    // Outdoor overrides
    val OutdoorBg      = Color(0xFFFFF8EA)
    val OutdoorWater   = Color(0xFF005BBB)
    val OutdoorBlocked = Color(0xFF9B1C1C)
    val OutdoorOk      = Color(0xFF0F6B2F)
}

val LightColors: ColorScheme = lightColorScheme(
    primary            = SproutColors.Humus,
    onPrimary          = SproutColors.Oat,
    primaryContainer   = SproutColors.Surface,
    onPrimaryContainer = SproutColors.Humus,

    secondary            = SproutColors.Water,
    onSecondary          = Color.White,
    secondaryContainer   = SproutColors.WaterTint,
    onSecondaryContainer = SproutColors.WaterDeep,

    tertiary            = SproutColors.Moss,
    onTertiary          = Color.White,
    tertiaryContainer   = SproutColors.Seed,
    onTertiaryContainer = Color(0xFF243D04),

    background       = SproutColors.Oat,
    onBackground     = SproutColors.Humus,
    surface          = SproutColors.Surface,
    onSurface        = SproutColors.Humus,
    surfaceVariant   = Color(0xFFEDE4D6),
    onSurfaceVariant = Color(0xFF4B4540),

    outline        = SproutColors.Border,
    outlineVariant = SproutColors.BorderSubtle,

    error            = SproutColors.Blocked,
    onError          = Color.White,
    errorContainer   = SproutColors.BlockedTint,
    onErrorContainer = SproutColors.Blocked,
)

val DarkColors: ColorScheme = darkColorScheme(
    primary            = SproutColors.Oat,
    onPrimary          = SproutColors.Humus,
    primaryContainer   = Color(0xFF2A2724),
    onPrimaryContainer = SproutColors.Oat,

    secondary            = Color(0xFF7DB3FF),
    onSecondary          = Color(0xFF002C70),
    secondaryContainer   = Color(0xFF1D4ED8),
    onSecondaryContainer = SproutColors.WaterTint,

    tertiary            = SproutColors.Seed,
    onTertiary          = Color(0xFF243D04),
    tertiaryContainer   = Color(0xFF3A5610),
    onTertiaryContainer = SproutColors.Seed,

    background       = SproutColors.Graphite,
    onBackground     = Color(0xFFDFD8CC),
    surface          = Color(0xFF221F1C),
    onSurface        = Color(0xFFDFD8CC),
    surfaceVariant   = Color(0xFF2A2724),
    onSurfaceVariant = Color(0xFF8A8276),

    outline        = Color(0xFF6E675B),
    outlineVariant = Color(0xFF3A3631),

    error            = Color(0xFFFF8A7A),
    onError          = Color(0xFF5C0E04),
    errorContainer   = Color(0xFF8A2418),
    onErrorContainer = SproutColors.BlockedTint,
)

// Outdoor — NOT a Material standard variant. High-contrast for direct sunlight.
// Maximum legibility, black borders, +1sp text (handled in Type, not here).
val OutdoorColors: ColorScheme = lightColorScheme(
    primary            = Color.Black,
    onPrimary          = SproutColors.OutdoorBg,
    primaryContainer   = SproutColors.OutdoorBg,
    onPrimaryContainer = Color.Black,

    secondary            = SproutColors.OutdoorWater,
    onSecondary          = Color.White,
    secondaryContainer   = SproutColors.WaterTint,
    onSecondaryContainer = Color(0xFF003D80),

    tertiary            = Color(0xFF3E5234),
    onTertiary          = Color.White,
    tertiaryContainer   = Color(0xFF6B9F00),
    onTertiaryContainer = Color.Black,

    background       = SproutColors.OutdoorBg,
    onBackground     = Color.Black,
    surface          = Color.White,
    onSurface        = Color.Black,
    surfaceVariant   = Color(0xFFEFE2CD),
    onSurfaceVariant = Color(0xFF1A1A18),

    outline        = Color.Black,
    outlineVariant = Color(0xFF5E5348),

    error            = SproutColors.OutdoorBlocked,
    onError          = Color.White,
    errorContainer   = Color(0xFFFFDAD6),
    onErrorContainer = SproutColors.OutdoorBlocked,
)
