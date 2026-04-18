# CI Android para Pollen — workflow y regla de merge

**Fecha:** 2026-04-18
**Autor:** Cambium
**Area:** Infraestructura / CI
**Tipo:** Decision + implementacion

---

## Contexto

Floema trabaja Pollen en un entorno **sin Android SDK ni Gradle wrapper ejecutable**. Eso se ha manifestado en dos PRs consecutivos:

1. **PR #18 (bootstrap Pollen):** reconocio que "el CLI me protestó por falta del binario de Gradle precompilado" y valido "via asserts de introspeccion nativa de kotlinx". Lo aceptamos porque los schemas son declarativos: un bug habria sido evidente a ojo.
2. **PR #9 (UI splitscreen):** Floema declara que "no he podido compilar el submódulo de Android ni ejecutar sus tests de instrumentación. Mi entorno actual no tiene instalado el SDK de Android". El codigo toca **Compose con `LaunchedEffect`, ciclo de vida, recomposicion** — donde un bug es tan probable como el acierto.

La situacion es asimetrica entre devs:
- **Xilema** (Rhizome, Python) compila en su entorno y pasa 33/33 tests antes de PR.
- **Meristem** (Meristem, Python + FastAPI) compila en su entorno y pasa 20/20 tests antes de PR.
- **Floema** (Pollen, Android/Kotlin) **no puede compilar**. Push ciego.

Tres opciones evaluadas:

1. **Sustituir a Floema.** Descartado. La limitacion es de entorno, no de actitud. Ha aceptado feedback dos veces sin friccion, corrigio bitacora y convencion de identidad. Cambiarla a alguien con el mismo entorno tecnico no arregla nada.
2. **Revisor humano compila localmente.** Descartado. No escala, no registra, y convierte a Cambium en cuello de botella sincrono para cada push de Pollen.
3. **CI de GitHub Actions.** Elegida. Da a Floema un "entorno virtual" reproducible. Cada push dispara build + test. Si falla, los logs son publicos y ella itera.

## Que hicimos

### Workflow `.github/workflows/pollen-ci.yml`

- **Trigger:** `push` a ramas `feat/pollen-**` y `pull_request` a main cuando toca `code/pollen/**` o el propio workflow.
- **Runner:** `ubuntu-latest` con JDK 17 (Temurin), Android SDK (platforms;android-34 + build-tools;34.0.0), Gradle 8.6.
- **Pasos:**
  - `gradle assembleDebug` — compila APK debug
  - `gradle testDebugUnitTest` — corre tests JVM unitarios (no emulador)
  - Upload artifact con reportes de tests para inspeccion post-failure
- **No incluye:** tests de instrumentacion sobre emulador. Si llega a hacer falta (screenshot tests, tests de Compose en emulador), issue aparte.

### Regla nueva en `CONTRIBUTING.md §9.1`

**PR con CI en rojo no se mergea. Sin excepciones.** Si falla: leer logs, corregir, push, re-ejecuta automaticamente. Si el fallo es del workflow (no del codigo), issue aparte y PR en hold.

### Actualizacion `code/pollen/README.md`

Añadida seccion **Build local** con instrucciones para devs con Android SDK, y seccion **CI** explicando el workflow y que devs sin SDK pueden usar el CI como su entorno. Nota explicita de "si no tienes Android SDK local, usa el CI".

## Por que

### Por que Gradle 8.6 y no usar el wrapper

Floema no pudo generar `./gradlew` en su entorno, asi que el repo no tiene wrapper committeado. Opciones:
- **Commitear wrapper manualmente.** Implicaria que yo (Cambium) lo genere en mi entorno y lo commiteem, pero eso crea dependencia de que alguien con gradle lo mantenga.
- **Instalar Gradle en el CI.** `gradle/actions/setup-gradle@v3` con `gradle-version: '8.6'` provee `gradle` directamente en el PATH. No necesita wrapper.

Elegida la segunda. Si en el futuro una dev con Android Studio commitea el wrapper, el workflow funciona igual (basta con cambiar `gradle` por `./gradlew`).

### Por que no tests de instrumentacion en el CI

Android instrumented tests requieren emulador o dispositivo. En CI eso significa:
- Mas tiempo (emulador tarda 2-5 min en arrancar)
- Mas flakiness (timeouts, issues de display)
- Mas coste

No lo necesitamos para MVP. Los tests JVM unitarios de Compose cubren logica de recomposicion con `ComposeContentTestRule` sin emulador (si se usan). Si en v2 necesitamos screenshot tests reales, issue aparte.

### Por que trigger en push de `feat/pollen-**` ademas de PR

Floema queria feedback antes de abrir PR. Con trigger en push, cada vez que commitea y pushea su rama, el CI corre. Si falla, corrige sin haber abierto PR todavia. Reduce ruido en PRs.

### Por que el workflow solo cubre Pollen

Rhizome (Python) y Meristem (Python + FastAPI) se pueden testear en el entorno local de sus devs sin obstaculo. Xilema y Meristem ya pasan tests antes de PR. No necesitan CI todavia — lo bueno de CI para ellas seria regression detection cross-branch, pero es P2.

Issue aparte para montar CI Python cuando tenga prioridad (probablemente despues del MVP, si el codigo empieza a crecer).

## Proximos pasos

### Hoy (Cambium)

1. **Abrir PR #22** con este workflow. Cierra #21.
2. **Mergear #22** (si el propio workflow valida en el PR — se autocomprueba porque `.github/workflows/pollen-ci.yml` esta en los paths de trigger).
3. **Re-ejecutar CI sobre PR #9 de Floema** (push vacio o re-run manual). Si pasa verde, review + merge. Si falla, paso logs a Floema.

### Floema

1. Al ver este PR mergeado, en el proximo push a `feat/pollen-ui-splitscreen-9` (o trigger manual del workflow), verifica que el CI arranca.
2. Si el CI falla, itera con los logs hasta verde.
3. A partir de aqui, ningun PR de Pollen sin CI verde.

### Xilema / Meristem

Sin cambios. Siguen su flujo normal de tests locales.

## Riesgos asumidos

- **Coste de minutos CI.** GitHub Actions gratis da 2000 min/mes para repos publicos privados y **infinitos para repos publicos**. `sprout` es publico → coste cero.
- **CI lento (5-10 min estimado con cache en frio).** Se mitiga con cache de Gradle y dependencias. Ajustamos si se vuelve incomodo.
- **Version de Android SDK pinneada.** compileSdk=34, build-tools 34.0.0 hardcoded en el workflow. Si Floema bumpea versiones en `app/build.gradle.kts` sin bumpear el workflow, falla. Mitigacion: nota en el workflow y en el README de que estan acoplados. Alternativa futura: leer version desde `build.gradle.kts` — overkill hoy.

## Notas

- Esta entrada cumple la regla "PR no se mergea sin entrada en bitacora".
- Este issue (#21) es el primero de infra para zona compartida. Abrira la puerta a CI Rhizome y CI Meristem en issues separados cuando lleguen.

---

**Firma:** Cambium
**Revisado por:** Bea (aprobacion informal previa al merge, pendiente firma explicita)
