package net.sprout.pollen.sync

import retrofit2.converter.kotlinx.serialization.asConverterFactory
import kotlinx.serialization.json.Json
import net.sprout.pollen.schemas.FieldVisit
import net.sprout.pollen.schemas.PolicyPacket
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import java.util.concurrent.TimeUnit

interface MeristemApi {
    @POST("/visit")
    suspend fun uploadFieldVisit(@Body visit: FieldVisit)

    @GET("/policy/by-target/{id}")
    suspend fun getPolicyByTarget(@retrofit2.http.Path("id") id: String): PolicyPacket
    
    @GET("/health")
    suspend fun getHealth(): retrofit2.Response<Unit>
    
    @POST("/pollen/hello")
    suspend fun sendHello(@Body hello: PollenHello): retrofit2.Response<Unit>
    
    @POST("/pollen/heartbeat")
    suspend fun sendHeartbeat(@Body hello: PollenHello): retrofit2.Response<Unit>
    
    @POST("/pollen/bundles-pushed")
    suspend fun sendBundlesPushed(): retrofit2.Response<Unit>
    
    @POST("/pollen/policies-pulled")
    suspend fun sendPoliciesPulled(): retrofit2.Response<Unit>
}

class MeristemNetworkClient(baseUrl: String) : MeristemClient {
    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
    }

    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS) // Meristem could be slow
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(baseUrl)
        .client(okHttpClient)
        .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
        .build()

    private val api = retrofit.create(MeristemApi::class.java)

    override suspend fun uploadFieldVisit(visit: FieldVisit) {
        api.uploadFieldVisit(visit)
    }

    override suspend fun getLatestPolicy(targetId: String): PolicyPacket {
        return api.getPolicyByTarget(targetId)
    }

    override suspend fun checkHealth(): Boolean {
        return try {
            val response = api.getHealth()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }
    
    override suspend fun sendHello(hello: PollenHello): Boolean {
        return try {
            val response = api.sendHello(hello)
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }
    
    override suspend fun sendHeartbeat(hello: PollenHello): Boolean {
        return try {
            val response = api.sendHeartbeat(hello)
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }
    
    override suspend fun sendBundlesPushed(): Boolean {
        return try {
            val response = api.sendBundlesPushed()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }
    
    override suspend fun sendPoliciesPulled(): Boolean {
        return try {
            val response = api.sendPoliciesPulled()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }
}
