package net.sprout.pollen.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Save
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import net.sprout.pollen.PollenStore

@Composable
fun SettingsScreen(onBack: () -> Unit) {
    val context = LocalContext.current
    val store = remember { PollenStore(context) }

    var meristemUrl by remember { mutableStateOf(store.loadMeristemUrl()) }
    var rhizome01Url by remember { mutableStateOf(store.loadRhizomeUrl("01")) }
    var rhizome02Url by remember { mutableStateOf(store.loadRhizomeUrl("02")) }

    var meristemError by remember { mutableStateOf<String?>(null) }
    var rhizome01Error by remember { mutableStateOf<String?>(null) }
    var rhizome02Error by remember { mutableStateOf<String?>(null) }

    var lastSavedText by remember { mutableStateOf("Not saved yet") }

    fun validateUrl(url: String): String? {
        if (url.isBlank()) return "URL cannot be empty"
        if (!url.startsWith("http://") && !url.startsWith("https://")) return "Must start with http:// or https://"
        return null
    }

    fun normalizeUrl(url: String): String {
        return if (url.endsWith("/")) url else "$url/"
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text(
            text = "Settings",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground
        )
        Spacer(modifier = Modifier.height(24.dp))

        OutlinedTextField(
            value = meristemUrl,
            onValueChange = { meristemUrl = it; meristemError = null },
            label = { Text("Meristem URL") },
            placeholder = { Text("http://192.168.1.36:13000/") },
            isError = meristemError != null,
            supportingText = { meristemError?.let { Text(it) } },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = rhizome01Url,
            onValueChange = { rhizome01Url = it; rhizome01Error = null },
            label = { Text("Rhizome 01 URL") },
            placeholder = { Text("http://192.168.1.60:13010/") },
            isError = rhizome01Error != null,
            supportingText = { rhizome01Error?.let { Text(it) } },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = rhizome02Url,
            onValueChange = { rhizome02Url = it; rhizome02Error = null },
            label = { Text("Rhizome 02 URL (optional)") },
            placeholder = { Text("http://192.168.1.60:13020/") },
            isError = rhizome02Error != null,
            supportingText = { rhizome02Error?.let { Text(it) } },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.weight(1f))

        Button(
            onClick = {
                meristemError = validateUrl(meristemUrl)
                rhizome01Error = validateUrl(rhizome01Url)
                rhizome02Error = validateUrl(rhizome02Url)

                if (meristemError == null) {
                    store.saveMeristemUrl(normalizeUrl(meristemUrl))
                }
                if (rhizome01Error == null) {
                    store.saveRhizomeUrl("01", normalizeUrl(rhizome01Url))
                }
                if (rhizome02Error == null) {
                    store.saveRhizomeUrl("02", normalizeUrl(rhizome02Url))
                }

                if (meristemError == null && rhizome01Error == null && rhizome02Error == null) {
                    lastSavedText = "Just now"
                    onBack()
                }
            },
            modifier = Modifier.fillMaxWidth().height(56.dp)
        ) {
            Icon(Icons.Default.Save, contentDescription = "Save")
            Spacer(modifier = Modifier.width(8.dp))
            Text("Save URLs")
        }

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = "Last saved: $lastSavedText",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.outline,
            modifier = Modifier.align(Alignment.CenterHorizontally)
        )
    }
}
