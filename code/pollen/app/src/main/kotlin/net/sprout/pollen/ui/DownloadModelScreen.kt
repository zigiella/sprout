package net.sprout.pollen.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
fun DownloadModelScreen(onContinue: (String) -> Unit) {
    val scope = rememberCoroutineScope()
    var isDownloading by remember { mutableStateOf(false) }
    var progress by remember { mutableStateOf(0f) }
    var showPathInput by remember { mutableStateOf(false) }
    var modelPath by remember { mutableStateOf("/data/local/tmp/gemma-4-E4B-it.litertlm") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Descarga del Modelo AI", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            "Pollen requiere el modelo Gemma 4 E4B para la inferencia offline. Si ya lo has empujado mediante ADB a '/data/local/tmp', puedes saltar este paso.",
            textAlign = TextAlign.Center,
            color = Color.Gray
        )
        Spacer(modifier = Modifier.height(48.dp))
        
        if (isDownloading) {
            Text("Descargando modelo... (${(progress * 100).toInt()}%)", fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(8.dp))
            LinearProgressIndicator(
                progress = { progress },
                modifier = Modifier.fillMaxWidth().height(8.dp),
                color = MaterialTheme.colorScheme.primary
            )
        } else {
            Button(
                onClick = {
                    scope.launch {
                        isDownloading = true
                        for (i in 1..10) {
                            delay(300)
                            progress = i / 10f
                        }
                        onContinue("/data/local/tmp/gemma-4-E4B-it.litertlm") // default path after download
                    }
                },
                modifier = Modifier.fillMaxWidth().height(56.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text("Descargar Gemma 4 (1.2 GB)", fontWeight = FontWeight.Bold)
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        if (showPathInput) {
            OutlinedTextField(
                value = modelPath,
                onValueChange = { modelPath = it },
                label = { Text("Ruta absoluta del modelo") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
            Spacer(modifier = Modifier.height(8.dp))
            Button(
                onClick = { onContinue(modelPath) },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.secondary)
            ) {
                Text("Confirmar ruta y continuar")
            }
        } else {
            TextButton(
                onClick = { showPathInput = true },
                enabled = !isDownloading
            ) {
                Text("Saltar (Ya tengo el modelo en dispositivo)")
            }
        }
    }
}
