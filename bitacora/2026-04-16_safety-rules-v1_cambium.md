# Safety rules v1.0 — contrato de firmware ESP32

**Fecha:** 2026-04-16
**Autor:** Cambium
**Area:** Arquitectura / Seguridad fisica
**Tipo:** Decision (cierre de contrato)

---

## Contexto

Con `docs/20_data_contracts.md` ya cerrado, la pieza que queda para desbloquear el bootstrap completo de Rhizome es el **contrato de seguridad fisica**: que hace y que no hace el firmware del ESP32. `docs/10_rhizome_spec.md` §5.1 tenia un esbozo de reglas duras (bloquear si deposito <20%, 60s max, etc), pero no era un documento autoritativo ni completo.

Hoy lo cerramos como `docs/30_safety_rules.md` v1.0. Es el tercer documento de cabecera de la arquitectura (junto con `01_architecture.md` y `20_data_contracts.md`), y define la **frontera dura** entre software que razona y metal que actua.

## Que hicimos

Redactado `docs/30_safety_rules.md` v1.0 (~500 lineas). Establece:

### 1. Principios

- **Fail-safe por defecto.** Estado seguro = todo cerrado. Ante duda, cierra.
- **El firmware no confia en el Jetson.** Valida cada comando, trata al software como fuente potencialmente hostil.
- **Reglas en el metal, no en Python.** Si se cambia recompilando Python, no es regla dura. Hard rules solo se modifican reflasheando.
- **Observabilidad obligatoria.** Cada bloqueo, cada comando, cada evento al log NVS.
- **Boot en estado cerrado.** Power-on, reset, watchdog → todo LOW antes de procesar nada.

### 2. Maquina de estados de 5 estados

`BOOT → SAFE ↔ ACTIVE → ALERT → (recovery) → SAFE`, mas `DEGRADED` para fallos de sensor. Transiciones definidas duro, ninguna auto-recovery excepto `DEGRADED → SAFE` cuando el sensor vuelve (el resto requiere `RESET_ALERT` explicito con condicion recuperada).

### 3. Hard limits tabulados

- **Tiempo:** 60 s max por apertura, 30 s minimo entre aperturas, 8/hora, 48/dia.
- **Hidraulicos:** deposito >20%, caudal confirmado en 3 s o aborto, zonas simultaneas = 1.
- **Comunicacion:** heartbeat cada 5 s (timeout 10 s), 128 bytes max por mensaje, 10 CMD/s max.
- **Electricos:** temp interna <80 °C, 12V entre 10.5 y 13.5 V.

Precedencia explicita cuando varias reglas chocan.

### 4. Protocolo UART v1.0

Extensión del esbozo de `10_rhizome_spec.md` §5.1 con garantias duras:
- **CRC-8/DVB-S2** en cada mensaje. Descarte silencioso si no cuadra (sin NAK).
- **Seq number 16-bit modular** con deteccion de replay y saltos anomalos.
- **Codigos de REJECTED enumerados**: 12 codigos de rechazo conocidos, cerrados.
- Recuperacion tras corrupcion (descartar 256 bytes sin `\n` y esperar proximo).

### 5. Boot sequence dura

7 pasos. Pull-down pasivos hardware + LOW explicito en firmware ANTES de inicializar UART. 2 s de silencio inicial sin procesar comandos (drena basura del buffer mientras el Jetson arranca). Validacion de sensores criticos antes de entrar en SAFE.

### 6. Watchdog + brownout

Watchdog a 8 s, reset cada 2 s desde loop principal. Boot-loop detector: si reboota >3 veces en 60 s → `DEGRADED` permanente. Brownout detector a 2.9 V → reboot limpio en vez de estado indefinido.

### 7. Logging en NVS

Ring buffer de 4 KB en flash no-volatil. ~80-100 eventos retenidos. Rhizome drena via comando `DUMP_LOG` (periodic + on-demand tras cada ALERT). Sin esto, un ALERT deja de ser debuggeable post-mortem.

### 8. Lista explicita de lo que el LLM **no puede hacer**

Por construccion: no existe comando UART para cambiar limites, desactivar watchdog, abrir dos zonas, hacer RESET_ALERT con condicion activa, ni reflashear firmware. OTA **deshabilitado en v1.0** (seria vector de escalada). La unica forma de cambiar reglas duras es acceso fisico + reflash + bitacora firmada.

### 9. Testing obligatorio

15 tests minimos tabulados (`test_duration_over_max`, `test_deposit_low`, `test_rate_limit_hour`, `test_flow_fault`, `test_heartbeat_loss`, `test_boot_guard`, `test_alert_stuck`, `test_reboot_safe`, etc). Todos deben pasar **sobre hardware real** antes de cada release, y documentarse en bitacora con SHA del firmware.

Hay simulador (`mock_esp32.py`) para CI y desarrollo en viaje, pero los tests contra hardware real son no negociables.

## Por que

### Por que un documento aparte y no seccion de `10_rhizome_spec.md`

Porque las reglas de seguridad afectan a **los tres nodos**, no solo Rhizome:
- Xilema implementa el firmware.
- Floema necesita conocer los limites al disenar la UI de Pollen (p.ej. si la politica pide `water_duration_s: 120`, Pollen tiene que saber que Rhizome lo va a rechazar y mostrarlo en rojo antes de enviar).
- Meristem tiene que respetar los limites al emitir `PolicyPacket` (no generar politicas con `duration > 60s`).

Separarlo en `30_safety_rules.md` lo hace accesible a todas sin tener que abrir un spec de 400 lineas de otro nodo.

### Por que tan conservador en los limites

- **60 s max por apertura:** investigué documentacion agronomica de riego por goteo en maceteros. El riego mas largo "normal" es ~40 s. 60 s es margen razonable. Cualquier cosa mas alla es anomalia por definicion — mejor cortar y emitir alerta que intentar adivinar si es intencional.
- **20% deposito:** protege la bomba sumergible. Una bomba en seco se quema en minutos. El 20% es el umbral conservador documentado en datasheets de la familia DFRobot FIT05xx.
- **8/hora, 48/dia:** caps que cubren cualquier escenario de riego realista con holgura (>3x lo tipico). Mas que eso es LLM en bucle o politica defectuosa.
- **1 zona simultanea:** simplifica presupuesto hidraulico y evita dimensionar la bomba para peor caso (dos zonas + presion suficiente en ambas). Sobre una parcela con dos maceteros, regar secuencial es aceptable.

### Por que no OTA en v1.0

OTA (over-the-air firmware update) es el vector ideal para bypass de toda esta seguridad. Si Gemma decidiera un dia que "un firmware ligeramente modificado resuelve este problema" y existiera OTA, podria en teoria servir firmware por HTTP y el ESP32 lo aceptaria. **Sin OTA, el unico modo de cambiar reglas duras es acceso fisico al USB del ESP32.** 

Cuando en v2 queramos OTA (para field updates reales), se anade firma de firmware con clave publica pre-flasheada y el firmware valida la firma antes de aceptar actualizacion. En v1.0 no lo necesitamos: seguimos en fase de desarrollo, reflasheamos manualmente.

### Por que CRC-8 y no CRC-16

Mensajes <128 bytes. CRC-8 detecta todo error de 1 bit y >99% de errores multi-bit en ese rango. CRC-16 daria ~0.01% mejor deteccion a cambio de 2 bytes mas por mensaje. No vale la pena.

### Por que el firmware descarta silenciosamente en CRC mismatch en vez de NAK

Protocolos chatty (con NAK, retry automatico, etc) son complejidad que no necesitamos. Si hay CRC mismatch, el Jetson lo detecta por timeout (no recibe ACK en 500 ms) y hace retry a su nivel. Mas simple, menos codigo en el firmware, misma fiabilidad efectiva.

### Por que la lista explicita de "lo que el LLM no puede hacer"

Porque es parte del pitch narrativo del proyecto. "Sprout toma decisiones con LLM" suena peligroso si no se explica la capa de seguridad. Este documento es **prueba escrita** de que la seguridad no depende del LLM se comporte bien. Para el writeup y para el video, poder apuntar a esta seccion y decir "este es nuestro sandboxing fisico" es potente.

## Proximos pasos (hard commits)

### Xilema (Rhizome / Firmware)

1. **Implementar firmware ESP32 v1.0** en `code/rhizome/firmware/`. Arduino framework o ESP-IDF (eleccion de Xilema, ambos validos). Hito: los 15 tests de §8.2 pasan contra hardware real.
2. **Implementar `esp32_bridge.py`** en `code/rhizome/<module>/` con parseo del protocolo UART, calculo de CRC-8, gestion de seq numbers y timeouts.
3. **`mock_esp32.py`** en `code/rhizome/tests/firmware/` para CI: maquina de estados sin hardware, para poder testear Rhizome sin el Jetson enchufado al ESP32 fisico.
4. **Bitacora de benchmark** tras montar el test bench: documentar que los 15 tests pasan y el SHA del firmware validado.

### Floema (Pollen)

1. **Al disenar UI de envio de comandos/politicas** a Rhizome: respetar los limites duros en validacion cliente. P. ej. si usuaria introduce `duration_s: 90`, Pollen lo bloquea **antes** de intentar enviar, y explica "Rhizome rechazaria esto: el maximo es 60 s".
2. **Al mostrar `ContradictionAlert`** de tipo `RATE_LIMIT_*` o similar: explicar humano-legible que es un rechazo de capa fisica, no un bug del sistema.

### Dev Meristem (cuando entre)

1. Respetar los limites duros al generar `PolicyPacket`. Toda politica que genere valores >60 s de riego o >8 aperturas/hora es invalida.
2. Al recibir `ContradictionAlert` de tipo rate-limit: revisar la politica emitida, puede ser senal de bug estrategico.

### Cambium (yo)

1. **Abrir issues de backlog en GitHub** (pendiente con Bea de confirmar formato).
2. **Actualizar `10_rhizome_spec.md` §5.1** para que apunte a este documento como fuente autoritativa en vez de repetir reglas (evita drift).
3. **Refinar `docs/11_pollen_spec.md`** con BLE-discovery + WiFi-Direct + FastAPI (pendiente).
4. **Escribir `docs/40_naming_guidelines.md`** (Gemma naming compliance). Menos urgente, al final del sprint.

## Riesgos asumidos

- **Limites cerrados con valores conservadores antes de campo.** Riesgo: al probar en parcela real descubrimos que 60 s son pocos para un caso legitimo. Mitigacion: se bumpea a v1.1 con justificacion agronomica documentada y bitacora. El coste es reflashear.
- **No hay OTA.** Riesgo: field update fisico caro operativamente. Mitigacion: v2 con firma. En MVP no aplica porque no estamos desplegados en campo todavia.
- **Ring buffer de log es pequeno (4 KB).** Riesgo: en un incidente con muchos eventos se pierden los mas antiguos. Mitigacion: Rhizome drena cada hora, asi la ventana de perdida es <1h. Si en v1.x metemos SD card al ESP32, se amplia.
- **Tests requieren hardware real.** Riesgo: bottleneck en Xilema para releases. Mitigacion: tenemos simulador para iteracion rapida; hardware solo se usa para validacion pre-release.

## Notas

- Este documento cierra la triada de **documentos de cabecera** de Sprout: arquitectura (`01`), contratos de datos (`20`), contratos de seguridad (`30`). Son los tres que cualquier dev nueva tiene que leer antes de tocar codigo.
- No se reabre sin bitacora + firma Bea + Cambium.
- Esta entrada cumple la regla "PR no se mergea sin entrada en bitacora".

---

**Firma:** Cambium
**Revisado por:** Bea (pendiente confirmacion por digest 2026-04-17)
