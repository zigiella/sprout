package net.sprout.pollen.sync

import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import net.sprout.pollen.schemas.DecisionReceipt
import net.sprout.pollen.schemas.RhizomeSnapshot
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query
import java.util.concurrent.TimeUnit

@Serializable
data class ExplanationResponse(val explanation: String)

interface RhizomeApi {
    @GET("/status")
    suspend fun getStatus(): Map<String, String>

    @GET("/snapshot/latest")
    suspend fun getLatestSnapshot(): RhizomeSnapshot

    @GET("/receipts")
    suspend fun getReceipts(@Query("since") since: String? = null): List<DecisionReceipt>

    @GET("/explain/decision/{id}")
    suspend fun explainDecision(@Path("id") id: String): ExplanationResponse
}

class RhizomeNetworkClient(baseUrl: String) : RhizomeClient {
    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
    }

    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(baseUrl)
        .client(okHttpClient)
        .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
        .build()

    private val api = retrofit.create(RhizomeApi::class.java)

    override suspend fun getStatus(): Map<String, String> = api.getStatus()
    
    override suspend fun getLatestSnapshot(): RhizomeSnapshot = api.getLatestSnapshot()
    
    override suspend fun getReceipts(since: String?): List<DecisionReceipt> = api.getReceipts(since)
    
    override suspend fun explainDecision(id: String): String {
        return api.explainDecision(id).explanation
    }
}
