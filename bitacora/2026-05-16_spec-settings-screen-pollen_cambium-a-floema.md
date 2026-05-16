# Spec · SettingsScreen en Pollen para configurar URLs de Meristem y Rhizome — Cambium → Floema

**Fecha:** 2026-05-16 (día 31)
**Autora:** Cambium
**Para:** Floema (frente Pollen Android)
**Tema:** Spec de una pantalla Settings que permita al usuario del flavor device configurar en runtime las URLs de Meristem y Rhizome, sin tener que tocar el código y recompilar. Pregunta vino de Bea durante el cierre del día 31; gap real del MVP que conviene cerrar antes del 19 si te entra.

---

## Contexto

Bea pregunta cómo un usuario del flavor `device` indica la IP de su propio Meristem (y los Rhizomes que tenga). Cuando miramos el código:

- `VisitarMeristemScreen.kt:46` → `MeristemNetworkClient("http://192.168.1.36:13000/")` hardcoded.
- `VisitarRhizomeScreen.kt:46` → `RhizomeNetworkClient("http://192.168.1.60:$port/")` hardcoded (port 13010 / 13020 según plot).

No hay pantalla de Settings. No hay NsdManager / mDNS discovery en el código (a pesar de que el doc de arquitectura claimeaba lo contrario — eso ya lo corregí honestamente esta tarde en main).

Para un usuario real del device flavor APK que quiera apuntar a su propio Meristem hoy, el único camino es clonar repo, editar las dos líneas, rebuildear y side-loadear. Eso es un gap claro.

## Propuesta MVP (lo mínimo que cierra la pregunta de Bea)

Una pantalla Settings con dos campos de URL, persistencia simple en SharedPreferences vía `PollenStore`, y las dos `Visitar*Screen` leen del store.

### UI mínima

Pantalla nueva: `SettingsScreen.kt` en `code/pollen/app/src/main/kotlin/net/sprout/pollen/ui/`.

```
┌─────────────────────────────────────┐
│  ← Settings                          │
├─────────────────────────────────────┤
│                                      │
│  Meristem URL                        │
│  ┌──────────────────────────────┐    │
│  │ http://192.168.1.36:13000/   │    │
│  └──────────────────────────────┘    │
│  e.g. http://meristem.local:13000/   │
│  or  http://192.168.x.x:13000/       │
│                                      │
│  Rhizome 01 URL                      │
│  ┌──────────────────────────────┐    │
│  │ http://192.168.1.60:13010/   │    │
│  └──────────────────────────────┘    │
│                                      │
│  Rhizome 02 URL (optional)           │
│  ┌──────────────────────────────┐    │
│  │ http://192.168.1.60:13020/   │    │
│  └──────────────────────────────┘    │
│                                      │
│  [ Save ]                            │
│                                      │
│  Last saved: 2 minutes ago           │
└─────────────────────────────────────┘
```

Tres campos:
1. **Meristem URL** — base URL del nodo Meristem. Default: `http://192.168.1.36:13000/` (el actual hardcoded).
2. **Rhizome 01 URL** — base URL del Rhizome primario. Default: `http://192.168.1.60:13010/`.
3. **Rhizome 02 URL** — opcional, para multi-Rhizome demo. Default: `http://192.168.1.60:13020/`.

Botón `Save` que persiste y vuelve a Home.

### Validación mínima

Antes de guardar, validar que cada URL:
- Empieza por `http://` o `https://`
- Tiene una host válida (no vacía)
- Tiene un puerto válido si lo lleva (1-65535)
- Termina en `/` (o normalizar añadiéndolo)

Si alguna falla, mostrar error inline en el campo correspondiente. No bloquear el guardado por las que sí son válidas; solo el campo con error.

### Persistencia

`PollenStore.kt` ya usa SharedPreferences y tiene el patrón. Añadir tres métodos:

```kotlin
fun saveMeristemUrl(url: String) {
    prefs.edit().putString("meristem_url", url).apply()
}

fun loadMeristemUrl(): String {
    return prefs.getString("meristem_url", "http://192.168.1.36:13000/") ?: "http://192.168.1.36:13000/"
}

fun saveRhizomeUrl(plotId: String, url: String) {
    prefs.edit().putString("rhizome_url_${plotId}", url).apply()
}

fun loadRhizomeUrl(plotId: String): String {
    val default = if (plotId.contains("02"))
        "http://192.168.1.60:13020/"
    else
        "http://192.168.1.60:13010/"
    return prefs.getString("rhizome_url_${plotId}", default) ?: default
}
```

### Puntos de lectura (donde leer del store)

**`VisitarMeristemScreen.kt:46`** cambia de:
```kotlin
MeristemNetworkClient("http://192.168.1.36:13000/")
```
a:
```kotlin
val store = remember { PollenStore(context) }
MeristemNetworkClient(store.loadMeristemUrl())
```

**`VisitarRhizomeScreen.kt:46`** cambia de:
```kotlin
val port = if (plotId.contains("02")) "13020" else "13010"
RhizomeNetworkClient("http://192.168.1.60:$port/")
```
a:
```kotlin
val store = remember { PollenStore(context) }
RhizomeNetworkClient(store.loadRhizomeUrl(plotId))
```

### Acceso a Settings desde la UI

Un icono de engranaje en `HomeScreen.kt` top-right, o un menú overflow `⋮`. Tap abre `SettingsScreen`. Cuando vuelves, los datos del store ya están actualizados.

## Test plan

- [ ] Settings se abre desde Home, los campos vienen prellenados con los defaults
- [ ] Cambiar Meristem URL, Save, volver a Home, tap "Visitar Meristem" → el cliente HTTP apunta a la nueva URL
- [ ] Lo mismo para Rhizome 01 y 02
- [ ] URLs inválidas (sin esquema, host vacío) muestran error inline
- [ ] El flavor `demo` ignora estos campos (sigue usando `MeristemMockClient` y `RhizomeMockClient` — no hay regresión)
- [ ] Tras matar la app y reabrir, las URLs persisten
- [ ] Tras desinstalar el APK, los datos se borran (Android lo gestiona vía SharedPreferences scope)

## Por qué esto cierra la pregunta de Bea

Un usuario que descarga el device APK desde `sprout.zigiella.com/get/` y quiere conectarlo a su propio Meristem:

1. Instala el APK.
2. Side-loadea el modelo Gemma 4 E4B vía ADB (como ya está documentado).
3. Abre la app → engranaje → Settings.
4. Cambia las URLs a las suyas.
5. Save. Lo siguiente que haga (Visitar Meristem o Visitar Rhizome) ya va a sus servidores.

Sin recompilar nada. Ese es el cambio.

## Out of scope para este parche (deja para v1.1+)

- **mDNS auto-discovery.** Más invasivo (NsdManager API en Android, anuncio de servicios `_sprout-meristem._tcp` y `_sprout-rhizome._tcp` en el lado de Meristem y Rhizome). Lo dejamos para v1.1.
- **Botón "Test connection"** que haga un GET `/health` y muestre 🟢/🔴 inline. Nice to have. Si te entra rápido, adelante; si no, dropea.
- **Discovery de Rhizomes en la LAN.** Mismo argumento.
- **Múltiples Rhizomes más allá de 01/02.** El MVP ya solo demuestra interoperabilidad multi-Rhizome con `rhizome_02` como simulación host-side. Si quieres soportar N Rhizomes ahora, el patrón cambia (lista dinámica en lugar de dos campos fijos). Hablamos antes si quieres ese alcance.

## Coordinación

- Esto es 100% tu jurisdicción (Pollen Android). Yo no toco código de Pollen.
- Cuando empieces, abre rama nueva desde `main` actual (no desde `feat/floema/pollen-demo-signals` ni `feat/floema/gradle-apk-rename` — esas están viejas). Nombre sugerido: `feat/floema/settings-screen-urls`.
- Verifica con `git fetch origin && git log --oneline origin/main..HEAD` antes de pushear que no tienes commits viejos colgando del fork (el patrón de las dos rondas anteriores).
- Cuando abras PR, ping en chat y la mergeo si pinta bien o reviewamos juntas.

## Plazo

Tres días hasta el 19. No es urgente; si te entra hoy o mañana, mejor — cierra un gap real que Bea identificó. Si no llega, marcamos en el doc de arquitectura como "v1.1 confirmed roadmap" y queda como next-iteration honesta.

Gracias por sostener todo el frente Pollen.

— Cambium
