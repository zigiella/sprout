package net.sprout.pollen.sync

import kotlinx.coroutines.delay
import net.sprout.pollen.schemas.DecisionReceipt
import net.sprout.pollen.schemas.PolicyPacket
import net.sprout.pollen.schemas.RhizomeSnapshot
import okhttp3.OkHttpClient
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import java.io.IOException

interface RhizomeApi {
    @GET("/snapshot/latest")
    suspend fun getSnapshot(): RhizomeSnapshot

    @GET("/decision/latest")
    suspend fun getDecisionReceipt(): DecisionReceipt

    @POST("/policy")
    suspend fun pushPolicy(@Body packet: PolicyPacket): Response<Void>
}

class RhizomeNetworkClient(private val baseUrl: String) : RhizomeClient {

    private val api: RhizomeApi

    init {
        val okHttpClient = OkHttpClient.Builder().build()
        val retrofit = Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        api = retrofit.create(RhizomeApi::class.java)
    }

    override suspend fun getSnapshot(): RhizomeSnapshot {
        return api.getSnapshot()
    }

    override suspend fun getDecisionReceipt(): DecisionReceipt {
        return api.getDecisionReceipt()
    }

    override suspend fun pushPolicy(packet: PolicyPacket): Boolean {
        return retryWithBackoff {
            val response = api.pushPolicy(packet)
            if (!response.isSuccessful) {
                throw IOException("Failed to push policy: \${response.code()}")
            }
            true
        }
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
        return block() // Last attempt throws if it fails
    }
}
