package net.sprout.pollen.sync

import android.util.Log
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import java.util.concurrent.TimeUnit
import kotlinx.serialization.json.Json
import kotlinx.serialization.Serializable

@Serializable
data class MeristemCommand(
    val commandId: String,
    val type: String, // e.g. "REQUEST_SNAPSHOT", "REQUEST_RECEIPTS"
    val payload: String? = null
)

class MeristemSocketClient(
    private val wsUrl: String,
    private val onCommandReceived: (MeristemCommand) -> Unit
) {
    private val client = OkHttpClient.Builder()
        .readTimeout(0, TimeUnit.MILLISECONDS)
        .build()
        
    private var webSocket: WebSocket? = null
    private val json = Json { ignoreUnknownKeys = true }

    fun connect() {
        if (webSocket != null) return
        
        val request = Request.Builder()
            .url(wsUrl)
            .build()
            
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: okhttp3.Response) {
                Log.i("MeristemSocketClient", "Connected to Meristem WS: $wsUrl")
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                Log.d("MeristemSocketClient", "Message received: $text")
                try {
                    val command = json.decodeFromString<MeristemCommand>(text)
                    onCommandReceived(command)
                } catch (e: Exception) {
                    Log.e("MeristemSocketClient", "Failed to parse command", e)
                }
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                Log.i("MeristemSocketClient", "Connection closed: $reason")
                this@MeristemSocketClient.webSocket = null
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: okhttp3.Response?) {
                Log.e("MeristemSocketClient", "Connection failed", t)
                this@MeristemSocketClient.webSocket = null
            }
        })
    }

    fun disconnect() {
        webSocket?.close(1000, "Normal closure")
        webSocket = null
    }

    fun sendResponse(commandId: String, data: String) {
        val response = """{"responseTo": "$commandId", "data": $data}"""
        webSocket?.send(response)
    }
}
