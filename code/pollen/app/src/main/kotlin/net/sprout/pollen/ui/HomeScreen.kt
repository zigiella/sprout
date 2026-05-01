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
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            Text(stringResource(R.string.home_title), style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
            IconButton(onClick = { toggleLanguage(context) }) {
                Icon(Icons.Default.Language, contentDescription = "Cambiar Idioma")
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        Text(stringResource(R.string.home_my_plots), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.SemiBold)
        Spacer(modifier = Modifier.height(8.dp))
        
        Button(
            onClick = { onNavigateToRhizome("Rhizome_01") },
            modifier = Modifier.fillMaxWidth().height(56.dp)
        ) {
            Icon(Icons.Default.Nature, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Rhizome_01 (Parcela Norte)")
        }
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = { onNavigateToRhizome("Rhizome_02") },
            modifier = Modifier.fillMaxWidth().height(56.dp),
            colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.secondary)
        ) {
            Icon(Icons.Default.Nature, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Rhizome_02 (Parcela Sur)")
        }

        Spacer(modifier = Modifier.height(32.dp))
        Divider()
        Spacer(modifier = Modifier.height(32.dp))

        Text(stringResource(R.string.home_home_node), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.SemiBold)
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = onNavigateToMeristem,
            modifier = Modifier.fillMaxWidth().height(56.dp),
            colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.tertiary)
        ) {
            Icon(Icons.Default.Home, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Meristem (Ordenador Central)")
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
