package net.sprout.pollen.sync

import kotlinx.coroutines.delay
import retrofit2.converter.kotlinx.serialization.asConverterFactory
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import net.sprout.pollen.schemas.DecisionReceipt
import net.sprout.pollen.schemas.PolicyPacket
import net.sprout.pollen.schemas.RhizomeSnapshot
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query
import java.io.IOException
import java.util.concurrent.TimeUnit

@Serializable
data class ExplanationResponse(val explanation: String)

interface RhizomeApi {
    @GET("/status")
    suspend fun getStatus(): Map<String, String>

    @GET("/snapshot/latest")
    suspend fun getLatestSnapshot(): RhizomeSnapshot

    @GET("/receipts")
    suspend fun getReceipts(@Query("since") since: String? = null, @Query("locale") locale: String? = null): List<DecisionReceipt>

    @GET("/explain/decision/{id}")
    suspend fun explainDecision(@Path("id") id: String, @Query("locale") locale: String): ExplanationResponse

    @GET("/summary/since")
    suspend fun getSummarySince(@Query("since") since: String?, @Query("locale") locale: String): net.sprout.pollen.schemas.SummarySinceResponse
    
    @POST("/policy")
    suspend fun pushPolicy(@Body packet: PolicyPacket): Response<Void>
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

    override suspend fun getSnapshot(): RhizomeSnapshot = api.getLatestSnapshot()
    
    override suspend fun getDecisionReceipt(): DecisionReceipt = api.getReceipts(null, "en").first()

    override suspend fun pushPolicy(packet: PolicyPacket): Boolean {
        return retryWithBackoff {
            val response = api.pushPolicy(packet)
            if (!response.isSuccessful) {
                val errorBody = response.errorBody()?.string()
                throw IOException("Failed to push policy: ${response.code()}, body: $errorBody")
            }
            true
        }
    }

    override suspend fun getStatus(): Map<String, String> = api.getStatus()
    
    override suspend fun getLatestSnapshot(): RhizomeSnapshot = api.getLatestSnapshot()
    
    override suspend fun getReceipts(since: String?, locale: String): List<DecisionReceipt> = api.getReceipts(since, locale)
    
    override suspend fun explainDecision(id: String, locale: String): String {
        return api.explainDecision(id, locale).explanation
    }

    override suspend fun getSummarySince(since: String?, locale: String): net.sprout.pollen.schemas.SummarySinceResponse {
        return api.getSummarySince(since, locale)
    }

    private suspend fun <T> retryWithBackoff(
        maxRetries: Int = 3,
        initialDelayMs: Long = 500,
        factor: Double = 2.0,
        block: suspend () -> T
    ): T {
        var currentDelay = initialDelayMs
        repeat(maxRetries - 1) {
            try {
                return block()
            } catch (e: Exception) {
                delay(currentDelay)
                currentDelay = (currentDelay * factor).toLong()
            }
        }
        return block()
    }
}
