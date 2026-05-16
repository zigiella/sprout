package net.sprout.pollen

import android.content.Context
import kotlinx.serialization.json.Json
import kotlinx.serialization.encodeToString
import kotlinx.serialization.decodeFromString
import net.sprout.pollen.schemas.DecisionReceipt
import net.sprout.pollen.schemas.PolicyPacket
import net.sprout.pollen.schemas.RhizomeSnapshot

class PollenStore(context: Context) {
    private val prefs = context.getSharedPreferences("pollen_store", Context.MODE_PRIVATE)
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }

    fun saveSnapshot(snapshot: RhizomeSnapshot) {
        prefs.edit().putString("snapshot", json.encodeToString(snapshot)).apply()
    }
    
    fun loadSnapshot(): RhizomeSnapshot? {
        val str = prefs.getString("snapshot", null) ?: return null
        return try { json.decodeFromString<RhizomeSnapshot>(str) } catch (e: Exception) { null }
    }

    fun saveReceipts(receipts: List<DecisionReceipt>) {
        prefs.edit().putString("receipts", json.encodeToString(receipts)).apply()
    }
    
    fun loadReceipts(): List<DecisionReceipt> {
        val str = prefs.getString("receipts", null) ?: return emptyList()
        return try { json.decodeFromString<List<DecisionReceipt>>(str) } catch (e: Exception) { emptyList() }
    }
    
    fun savePolicy(policy: PolicyPacket) {
        prefs.edit().putString("policy", json.encodeToString(policy)).apply()
    }
    
    fun loadPolicy(): PolicyPacket? {
        val str = prefs.getString("policy", null) ?: return null
        return try { json.decodeFromString<PolicyPacket>(str) } catch (e: Exception) { null }
    }
    
    fun isModelDownloaded(): Boolean {
        return prefs.getBoolean("model_downloaded", false)
    }
    
    fun setModelDownloaded(downloaded: Boolean) {
        prefs.edit().putBoolean("model_downloaded", downloaded).apply()
    }
    
    fun getModelPath(): String {
        return prefs.getString("model_path", "/data/local/tmp/gemma-4-E4B-it.litertlm") ?: "/data/local/tmp/gemma-4-E4B-it.litertlm"
    }
    
    fun setModelPath(path: String) {
        prefs.edit().putString("model_path", path).apply()
    }

    fun saveMeristemUrl(url: String) {
        prefs.edit().putString("meristem_url", url).apply()
    }

    fun loadMeristemUrl(): String {
        return prefs.getString("meristem_url", "http://192.168.1.36:13000/") ?: "http://192.168.1.36:13000/"
    }

    fun saveRhizomeUrl(plotId: String, url: String) {
        prefs.edit().putString("rhizome_url_${plotId}", url).apply()
    }

    fun loadRhizomeUrl(plotId: String): String {
        val default = if (plotId.contains("02"))
            "http://192.168.1.60:13020/"
        else
            "http://192.168.1.60:13010/"
        return prefs.getString("rhizome_url_${plotId}", default) ?: default
    }
}
