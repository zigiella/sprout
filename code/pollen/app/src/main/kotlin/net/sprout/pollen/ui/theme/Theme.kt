package net.sprout.pollen.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable

@Composable
fun PollenTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    outdoorMode: Boolean = false, // Modo de alto contraste para el sol
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        outdoorMode -> OutdoorColors
        darkTheme -> DarkColors
        else -> LightColors
    }

    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}
