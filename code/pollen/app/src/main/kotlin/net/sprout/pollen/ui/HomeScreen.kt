package net.sprout.pollen.ui

import android.app.LocaleManager
import android.content.Context
import android.os.Build
import android.os.LocaleList
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.Nature
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import net.sprout.pollen.R

@Composable
fun HomeScreen(
    onNavigateToRhizome: (String) -> Unit,
    onNavigateToMeristem: () -> Unit
) {
    val context = LocalContext.current
    
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        // Header
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            Text(stringResource(R.string.home_title), style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onBackground)
            IconButton(onClick = { toggleLanguage(context) }) {
                Icon(Icons.Default.Language, contentDescription = "Cambiar Idioma", tint = MaterialTheme.colorScheme.onBackground)
            }
        }
        Spacer(modifier = Modifier.height(16.dp))

        // JurisdictionBanner
        Card(
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer),
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(
                text = stringResource(R.string.every_event_receipt),
                modifier = Modifier.padding(12.dp),
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onTertiaryContainer
            )
        }
        
        Spacer(modifier = Modifier.height(24.dp))

        // SectionLabel
        Text(
            text = "${stringResource(R.string.nearby_rhizomes).uppercase()} · 2", 
            style = MaterialTheme.typography.labelSmall, 
            color = MaterialTheme.colorScheme.outline
        )
        Spacer(modifier = Modifier.height(12.dp))
        
        // NodeCards
        NodeCard(title = "RHIZOME_01", subtitle = "Parcela Norte", onClick = { onNavigateToRhizome("Rhizome_01") })
        Spacer(modifier = Modifier.height(8.dp))
        NodeCard(title = "RHIZOME_02", subtitle = "Parcela Sur", onClick = { onNavigateToRhizome("Rhizome_02") })

        Spacer(modifier = Modifier.weight(1f))

        // MeristemCard
        Card(
            onClick = onNavigateToMeristem,
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Home, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text(stringResource(R.string.home_home_node), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(stringResource(R.string.meristem_sub), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.outline)
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Footer mono
        Text(
            text = stringResource(R.string.physical_prevails),
            style = MaterialTheme.typography.bodySmall, // Pretend it's mono
            color = MaterialTheme.colorScheme.outline,
            modifier = Modifier.fillMaxWidth(),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )
    }
}

@Composable
fun NodeCard(title: String, subtitle: String, onClick: () -> Unit) {
    Card(
        onClick = onClick,
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Nature, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onPrimaryContainer)
                Text(subtitle, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f))
            }
        }
    }
}

private fun toggleLanguage(context: Context) {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        val localeManager = context.getSystemService(LocaleManager::class.java)
        val current = localeManager.applicationLocales.toLanguageTags()
        val next = if (current == "es") "en" else "es"
        localeManager.applicationLocales = LocaleList.forLanguageTags(next)
    }
}
