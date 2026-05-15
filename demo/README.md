# demo/

Esta carpeta esta reservada para builds finales del APK Android de Pollen. Durante el ciclo del hackathon (30 dias) se decidio que la ruta publica de instalacion fuera **build desde codigo**, no APK pre-empaquetado. Las razones:

1. **Honestidad ante el evaluador.** El codigo se compila y se inspecciona; el APK firmado anade una capa de confianza sobre el binario que no es necesaria para un MVP.
2. **Tamano.** Un APK device-flavor pesa ~58 MB y requiere LFS o release attachment; el repo prefiere mantenerse ligero.
3. **Reproducibilidad.** `./gradlew assembleDemoDebug` desde `code/pollen/` es la fuente de verdad y siempre coincide con el codigo del repo.

## Build de la demo (sin modelo, ~30 MB)

```bash
cd code/pollen
./gradlew assembleDemoDebug
adb install app/build/outputs/apk/demo/debug/app-demo-debug.apk
```

Mock LiteRT determinista — no necesita el modelo de 3 GB. Sirve para recorrer la UI, el flujo de voz y los caminos de refusal/retry.

## Build device con Gemma 4 E4B real

```bash
cd code/pollen
./gradlew assembleDeviceRelease
adb push gemma-4-E4B-it.litertlm /data/local/tmp/gemma-4-E4B-it.litertlm
adb install app/build/outputs/apk/device/release/app-device-release.apk
```

Requiere Android 12+ / API 31+, 12 GB RAM recomendado, 6 GB libres. Ver [`code/pollen/README.md`](../code/pollen/README.md) para los pasos completos de side-load del modelo y permisos.

## Note on language

The public install path lives in the root [README](../README.md) and [SUBMISSION.md](../SUBMISSION.md) in English. This file documents the working decision around APK packaging in Spanish, the team's working language. See the [Language note](../README.md#language-note) for the project-wide policy.
