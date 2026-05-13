# [Feature Request] Expose reasoning/thinking tokens as a separate channel in LiteRT-LM Android API

**Title:** Expose reasoning/thinking tokens as a separate field or channel in the Android API when `enable_thinking` is true

**Environment:**
- LiteRT-LM Android SDK (0.1.0-alpha)
- Model: Gemma 4 E2B/E4B
- Backend: CPU / NPU

**Description:**
Currently, when initializing a `ConversationConfig` with `extraContext = mapOf("enable_thinking" to true)`, the model successfully generates reasoning tokens before the final output. However, the Android API (`Conversation.sendMessageAsync`) yields these reasoning tokens mixed into the same `Content.Text` stream as the final response. 

There is no structural separation (e.g., a `thinkingContent` field vs a `textContent` field) in the `Message` or `Chunk` objects returned by the SDK.

**Use Case:**
In our project (an offline agricultural assistant), we rely heavily on the agent's internal reasoning to make correct decisions (e.g., auditing sensor data). However, the end-user (a farmer operating a tablet in the field) should **only** see the final output, not the verbose reasoning process. 
Because the reasoning and the output are concatenated in the same string, we are forced to either:
1. Use complex regex to parse and hide the reasoning block.
2. Disable thinking entirely for conversational UI flows to avoid polluting the chat history and exceeding the KV cache limits in multi-turn interactions.

**Expected Behavior:**
Similar to how Ollama handles this via its API (returning a filled `thinking` field and a separate `content` field), the LiteRT-LM Android SDK should expose a way to distinguish which tokens belong to the reasoning phase and which belong to the final output generation.

**Proposed Solution:**
- Add a `thinkingText: String?` field to `Content.Text` or `Message`.
- OR emit a specific type of `Content` chunk (e.g., `Content.Reasoning`) during the thinking phase.

**Reproduction Steps:**
1. Load `gemma4:e2b` via LiteRT-LM.
2. `ConversationConfig(extraContext = mapOf("enable_thinking" to true))`
3. `sendMessageAsync("Evaluate this data...")`
4. Observe that the returned string contains both the internal thought process and the final JSON/Text combined.
