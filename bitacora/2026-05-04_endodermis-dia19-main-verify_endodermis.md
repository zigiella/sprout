# Dia 19 - Verificacion PRs mergeados desde main

**Autora:** Endodermis
**Fecha:** 2026-05-04
**Dia de proyecto:** 19
**Rama:** `feat/endodermis/jetson-day19-main-verify`

## 1. Arranque

Mensaje de Cambium recibido.

PRs relevantes ya mergeadas en `main`:

- #68 BME280 estable (`d0e72ac`)
- #69 perfiles Jetson (`c2c85bb`)
- #70 primer ping Jetson-ESP32 (`d090972`)

Local:

- `main` actualizado a `dfef91d`
- autor local configurado como `Endodermis <endodermis@sprout.local>`

Jetson:

- `~/sprout` actualizado de `2e19178` a `dfef91d`
- `rhizome_01` pertenece a `docker` y `dialout`
- no habia contenedores Sprout vivos al empezar

## 2. Lectura de Xilema antes de tocar Jetson

Leo `bitacora/2026-05-03_jetson-esp32-primer-ping_xilema.md`.

Hallazgos relevantes:

- Jetson detecto ESP32 en `/dev/ttyACM0`.
- El bloqueo fue permiso `dialout`, ya resuelto.
- Se valido `STATUS`, `HOST_HEARTBEAT`, `TELEMETRY`, `WATER A 12` rechazado
  por `TANK_LOW`, `ALERT_LATCHED` y `RESET_ALERT`.
- No hubo bomba, reles ni 12V.

Decision mia:

- no abrir `/dev/ttyACM0`;
- no repetir ping;
- no tocar firmware ni frontera fisica.

## 3. Scripts Jetson desde main

Ejecuto desde `~/sprout/code/rhizome/jetson`:

```bash
./collect_baseline.sh
./run_runtime.sh safe-cpu
./start_adapter.sh
./smoke_adapter.sh
LABEL=day19_main_verify ./run_battery.sh critical --dry-run
```

Resultados:

| Paso | Resultado |
|---|---|
| baseline | OK |
| `safe-cpu` | health OK |
| adapter | health OK |
| smoke safe-cpu | JSON OK |
| critical dry-run | lista RD01, RD03, RD08, RA02, RA04, RH02 |

Baseline destacada:

| Campo | Valor |
|---|---|
| Jetson Linux | R36.4.7 |
| RAM available inicial | ~5.7 GiB |
| Swap usada inicial | 0 |
| `CmaFree` inicial | ~222 MiB |
| Docker runtime | `nvidia` disponible, default `runc` |

## 4. `gpu-experimental` desde main

Ejecuto:

```bash
./run_runtime.sh gpu-experimental
```

Resultado:

```text
NvMapMemAllocInternalTagged: ... error 12
cudaMalloc failed: out of memory
failed to allocate CUDA0 buffer
failed to load model
```

Lectura:

- confirma que `gpu-experimental` no es runtime-pass garantizado;
- aunque dia 18 cargo con `--fit off --no-op-offload`, el perfil sigue siendo
  sensible al estado de memoria contigua/NvMap;
- se refuerza la decision de no usar GPU para rodaje ni demo contractual.

## 5. Restauracion

Restauro inmediatamente:

```bash
./run_runtime.sh safe-cpu
./smoke_adapter.sh
```

Resultado:

| Paso | Resultado |
|---|---|
| `safe-cpu` | health OK |
| adapter | seguia vivo |
| smoke restaurado | JSON OK |

Estado final:

```text
sprout-llama-e2b      Up, safe-cpu
sprout-adapter-12000  Up, llamacpp
```

## 6. Ajuste documental

Actualizo:

- `code/rhizome/jetson/README.md`
- `code/rhizome/jetson/run_runtime.sh`

Cambios:

- `gpu-experimental` queda descrito como perfil experimental que puede fallar
  por memoria contigua;
- `run_runtime.sh gpu-experimental` imprime preflight informativo de memoria
  (`MemAvailable`, `CmaFree`, `tegrastats`);
- README indica restaurar `safe-cpu` si falla.

## 7. Veredicto dia 19

`safe-cpu` desde `main`: **PASS**.

`gpu-experimental` desde `main`: **FAIL intermitente / no demo-safe**.

La conclusion de dia 18 se endurece:

> El perfil rapido no solo debe conservar contrato; tambien debe arrancar de
> forma repetible. Hasta entonces, `safe-cpu` manda.

---

## 8. Bateria real segun peticion de Xilema

Xilema pide:

1. repetir `safe-cpu`;
2. correr `run_battery.sh critical`;
3. si pasa, correr `run_battery.sh full`;
4. documentar resultado.

Ejecuto desde `main` en Jetson:

```bash
cd ~/sprout/code/rhizome/jetson
./run_runtime.sh safe-cpu
./start_adapter.sh
./smoke_adapter.sh
LABEL=day19_main_safe_cpu ./run_battery.sh critical
```

Resultado primera pasada:

| Prompt | envelope | status | duration_ms |
|---|---:|---:|---:|
| RD01 | OK | OK | 52569 |
| RD03 | OK | OK | 16449 |
| RD08 | OK | OK | 20148 |
| RA02 | OK | OK | 13242 |
| RA04 | OK | OK | 12909 |
| RH02 | FAIL | FAIL | 26840 |

Fallo RH02:

```text
done_reason=stop
tokens_out=172
parse_error=json_error: Expecting ',' delimiter
```

Contenido: JSON casi completo, sin fence, pero falta una llave final de cierre.

Repito una segunda vez:

```bash
LABEL=day19_main_safe_cpu_repeat ./run_battery.sh critical
```

Resultado segunda pasada:

| Prompt | envelope | status | duration_ms |
|---|---:|---:|---:|
| RD01 | OK | OK | 18033 |
| RD03 | OK | OK | 16447 |
| RD08 | OK | OK | 20629 |
| RA02 | OK | OK | 13155 |
| RA04 | OK | OK | 13095 |
| RH02 | FAIL | FAIL | 27337 |

No ejecuto `full` porque `critical` no pasa.

Telemetria posterior:

```text
RAM 3237/7620MB
SWAP 91/3810MB
cpu ~44 C
gpu ~44 C
VDD_IN ~3.1 W
```

Lectura:

- `safe-cpu` sigue arrancando y respondiendo smoke correctamente;
- los 5 casos de decision/safety pasan;
- RH02 queda sensible tambien en `safe-cpu` desde `main`;
- no hay riesgo fisico directo porque RH02 es handoff/summarize, no comando
  de riego;
- aun asi, no se debe vender "critical 6/6" hoy.

## 9. Ajuste al helper de bateria

`run_battery.sh` no debe devolver exito si el harness imprime mismatch.
Actualizo el script para validar el JSONL al terminar:

- error HTTP -> fallo;
- `envelope_valid=false` -> fallo;
- `status_match` incorrecto -> fallo.

En modo `full`, si `critical` falla, `remaining` no se ejecuta.

Decision:

- mejor que la automatizacion sea estricta;
- si el LLM se comporta de forma segura pero fuera de contrato, lo vemos como
  fallo de bateria y no como pass silencioso.
