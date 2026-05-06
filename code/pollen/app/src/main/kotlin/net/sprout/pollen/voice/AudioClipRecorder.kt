package net.sprout.pollen.voice

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import androidx.core.content.ContextCompat
import java.io.File
import java.io.FileOutputStream
import java.io.RandomAccessFile
import java.util.concurrent.atomic.AtomicLong
import kotlin.concurrent.thread

class AudioClipRecorder(private val context: Context) {
    private var audioRecord: AudioRecord? = null
    private var writerThread: Thread? = null
    private var outputFile: File? = null
    private val bytesWritten = AtomicLong(0L)

    @Volatile
    private var recording = false

    @SuppressLint("MissingPermission")
    fun start(): File {
        require(!recording) { "Ya hay una grabacion en curso." }
        require(hasRecordAudioPermission()) { "Falta permiso de microfono." }

        val audioDir = File(context.cacheDir, AUDIO_DIR_NAME).apply { mkdirs() }
        val file = File(audioDir, "voice-${System.currentTimeMillis()}.wav")
        val minBufferSize = AudioRecord.getMinBufferSize(
            SAMPLE_RATE,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
        )
        require(minBufferSize > 0) { "No se pudo preparar el microfono." }

        val bufferSize = maxOf(minBufferSize, DEFAULT_BUFFER_SIZE)
        val recorder = AudioRecord.Builder()
            .setAudioSource(MediaRecorder.AudioSource.VOICE_RECOGNITION)
            .setAudioFormat(
                AudioFormat.Builder()
                    .setSampleRate(SAMPLE_RATE)
                    .setChannelMask(AudioFormat.CHANNEL_IN_MONO)
                    .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                    .build(),
            )
            .setBufferSizeInBytes(bufferSize)
            .build()

        require(recorder.state == AudioRecord.STATE_INITIALIZED) {
            recorder.release()
            "No se pudo inicializar la grabadora."
        }

        bytesWritten.set(0L)
        recording = true
        outputFile = file
        audioRecord = recorder

        val output = FileOutputStream(file)
        output.write(ByteArray(WAV_HEADER_BYTES))
        recorder.startRecording()
        writerThread = thread(name = "pollen-audio-recorder") {
            val buffer = ByteArray(bufferSize)
            try {
                while (recording) {
                    val read = recorder.read(buffer, 0, buffer.size)
                    if (read > 0) {
                        output.write(buffer, 0, read)
                        bytesWritten.addAndGet(read.toLong())
                    }
                }
            } finally {
                output.flush()
                output.close()
            }
        }
        return file
    }

    fun stopAndSave(): File {
        val file = requireNotNull(outputFile) { "No hay grabacion activa." }
        recording = false
        runCatching { audioRecord?.stop() }
        writerThread?.join(STOP_TIMEOUT_MS)
        runCatching { audioRecord?.release() }
        audioRecord = null
        writerThread = null
        outputFile = null

        val dataLength = bytesWritten.get()
        require(dataLength >= MIN_AUDIO_BYTES) {
            file.delete()
            "La grabacion es demasiado corta."
        }
        writeWavHeader(file, dataLength)
        return file
    }

    fun cancel() {
        val file = outputFile
        recording = false
        runCatching { audioRecord?.stop() }
        writerThread?.join(STOP_TIMEOUT_MS)
        runCatching { audioRecord?.release() }
        audioRecord = null
        writerThread = null
        outputFile = null
        file?.delete()
    }

    private fun hasRecordAudioPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.RECORD_AUDIO,
        ) == PackageManager.PERMISSION_GRANTED
    }

    private fun writeWavHeader(file: File, dataLength: Long) {
        RandomAccessFile(file, "rw").use { wav ->
            wav.seek(0)
            wav.writeAscii("RIFF")
            wav.writeIntLe((36L + dataLength).toInt())
            wav.writeAscii("WAVE")
            wav.writeAscii("fmt ")
            wav.writeIntLe(16)
            wav.writeShortLe(1)
            wav.writeShortLe(1)
            wav.writeIntLe(SAMPLE_RATE)
            wav.writeIntLe(SAMPLE_RATE * BYTES_PER_SAMPLE)
            wav.writeShortLe(BYTES_PER_SAMPLE)
            wav.writeShortLe(BITS_PER_SAMPLE)
            wav.writeAscii("data")
            wav.writeIntLe(dataLength.toInt())
        }
    }

    private fun RandomAccessFile.writeAscii(value: String) {
        write(value.toByteArray(Charsets.US_ASCII))
    }

    private fun RandomAccessFile.writeIntLe(value: Int) {
        write(byteArrayOf(
            (value and 0xff).toByte(),
            ((value shr 8) and 0xff).toByte(),
            ((value shr 16) and 0xff).toByte(),
            ((value shr 24) and 0xff).toByte(),
        ))
    }

    private fun RandomAccessFile.writeShortLe(value: Int) {
        write(byteArrayOf(
            (value and 0xff).toByte(),
            ((value shr 8) and 0xff).toByte(),
        ))
    }

    companion object {
        private const val AUDIO_DIR_NAME = "voice"
        private const val SAMPLE_RATE = 16_000
        private const val BITS_PER_SAMPLE = 16
        private const val BYTES_PER_SAMPLE = 2
        private const val DEFAULT_BUFFER_SIZE = 4096
        private const val MIN_AUDIO_BYTES = SAMPLE_RATE * BYTES_PER_SAMPLE / 3
        private const val STOP_TIMEOUT_MS = 3_000L
        private const val WAV_HEADER_BYTES = 44
    }
}
