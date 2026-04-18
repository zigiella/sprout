package net.sprout.pollen

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import net.sprout.pollen.ui.SplitscreenDash
import net.sprout.pollen.ui.PollenViewModel
import net.sprout.pollen.inference.GemmaEngine

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val engine = GemmaEngine(this)
        val viewModel = PollenViewModel(engine)

        setContent {
            MaterialTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    SplitscreenDash(viewModel)
                }
            }
        }
    }
}
