package net.sprout.pollen.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import net.sprout.pollen.schemas.DecisionReceipt
import net.sprout.pollen.schemas.PolicyPacket

@Composable
fun AuditLogScreen(
    receipts: List<DecisionReceipt>,
    policy: PolicyPacket?
) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("Historial (Log de Auditoría)", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(16.dp))
        
        Text("Política Activa en Tránsito", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
        if (policy != null) {
            Card(
                modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Policy ID: ${policy.policyId}", fontWeight = FontWeight.Bold)
                    val budgetText = policy.rules.dailyWaterBudgetLiters?.toString() ?: policy.rules.dailyBudgetMl?.let { (it / 1000f).toString() } ?: "?"
                    Text("Budget: $budgetText L")
                    if (policy.rules.requireVisionConfirmation == true) {
                        Text("⚠️ REQUIRE VISION CONFIRMATION", color = MaterialTheme.colorScheme.error, fontWeight = FontWeight.Bold)
                    }
                }
            }
        } else {
            Text("Ninguna política cargada.")
        }

        Spacer(modifier = Modifier.height(16.dp))
        Text("Eventos de Campo", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
        
        LazyColumn {
            items(receipts) { receipt ->
                Card(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(receipt.action.name, fontWeight = FontWeight.Bold)
                        Text(receipt.createdAt, style = MaterialTheme.typography.bodySmall)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(receipt.rationaleShort)
                    }
                }
            }
        }
    }
}
