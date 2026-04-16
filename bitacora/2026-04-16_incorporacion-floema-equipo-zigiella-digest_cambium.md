# Incorporacion de Floema + equipo zigiella + limpieza repo publico + digest diario

**Fecha:** 2026-04-16
**Autor:** Cambium
**Area:** General
**Tipo:** Decision + Aprendizaje

---

## Contexto

Bea confirma cambios organizativos importantes:
- **Floema** se suma al equipo. Se encarga de Pollen. Ya tiene el repo clonado.
- Somos 4: Bea (project lead), Cambium (coordinacion + diseno), Xilema (Rhizome), Floema (Pollen).
- Bea y Cambium cubrimos todo lo demas (research, writeup, video, demo).
- Autoria publica: **equipo zigiella**. Sin nombres individuales visibles en README ni contribuidoras de GitHub.
- Quitar toda referencia externa (hackathon, plataforma de entrega, premios) del repo publico. Razon: no queremos ser encontradas todavia via busquedas.
- Cambium asume **supervision de calidad** de Xilema y Floema (review de PRs, consistencia con arquitectura y schemas).
- **Decisiones estrategicas** quedan entre Bea y Cambium.
- Bea propone: **digest diario por email** en lenguaje accesible y pedagogico.

## Que hicimos

### 1. Incorporacion de Floema

- Floema = Dev Pollen (Pixel 10 Pro + LiteRT + llama.cpp fallback).
- Mismo contrato de trabajo que Xilema: git-based, ramas `feat/pollen-<tema>`, PR contra `main`, regla de no mergear sin entrada en bitacora.
- Lee como onboarding: `docs/11_pollen_spec.md` + bitacora `2026-04-15_respuesta-xilema-6-decisiones_cambium.md` (las 6 decisiones valen tambien para ella: schemas, frontera Pollen↔Rhizome, fiabilidad > pureza, razonamiento estructurado).
- Primera tarea sugerida: bootstrap de `code/pollen/` con skeleton Android + mocks de sync contra Rhizome (esperando que yo cierre los schemas en `docs/20_data_contracts.md` esta semana).

### 2. Identidad publica: "equipo zigiella"

- README.md: seccion "Contexto: Gemma 4 Good Hackathon" eliminada. Anadido bloque "Autoria — Mantenido por equipo zigiella".
- CONTRIBUTING.md: reescrito como "guia interna del equipo zigiella". Tabla de roles sin nombres propios (solo funciones: "Coordinacion y diseno", "Dev Rhizome", "Dev Pollen", "Dev Meristem"). Quitadas filas de "Redactoras / Investigadoras / Grabacion" — ese trabajo lo cubre el core.
- Commits siguen firmados con codenames (Cambium, Xilema, Floema) — son nombres vegetales neutros, no identifican personas fisicas. Aceptable.

### 3. Limpieza de referencias externas

Cirugia quirurgica sobre 14 archivos. Reemplazos tipicos:
- "hackathon" → "proyecto" / "MVP"
- "jurado" → "lector externo" / "quien mira"
- "writeup de Kaggle" → "writeup"
- "Global Resilience / Ollama track / LiteRT track / Unsloth track" → fuera
- "deadline 18 mayo 2026" → fuera
- "$200k prize pool" → fuera

Archivo eliminado del repo: `HACKATHON.md` (guardado como copia privada en `C:\Users\Usuario\Desktop\CAJON\HACKATHON_interno_no_publicar.md` para referencia del equipo core).

**Lo que NO toqué:** las 3 bitacoras anteriores a hoy. Razones:
- Son diario interno, no pagina de aterrizaje.
- Reescribir el historial de git por esas menciones seria invasivo (rewrite, force-push, cache GitHub).
- Los motores de busqueda indexan menos las carpetas profundas que README/CONTRIBUTING.
- Si en algun momento quereis limpieza total, se puede hacer con `git filter-repo` antes de publicar el repo fuera de nuestro circulo.

### 4. Rol de supervision de calidad (Cambium)

Asumido formalmente. Incluye:
- Review tecnico de cada PR de Xilema y Floema antes de merge.
- Chequeo de que cada PR tenga entrada en bitacora asociada.
- Chequeo de consistencia con schemas de `docs/20_data_contracts.md` (cuando existan).
- Chequeo de que los codenames se mantienen (no leaks de nombres reales en codigo, comentarios o commits).
- Si hay desacuerdo tecnico fuerte entre Xilema/Floema y Cambium, escalada a Bea.

### 5. Decisiones estrategicas

Toda decision de alcance, timing, narrativa, presupuesto o equipo queda entre **Bea + Cambium**. Las dev (Xilema, Floema) opinan en su ambito tecnico y pueden proponer, pero no deciden perimetro.

### 6. Digest diario por email

**Propuesta respondida a Bea** (ver resumen al final de esta entrada). Mi recomendacion: **si, pero con mecanica clara**:
- Yo escribo el borrador cada dia al cerrar sesion de trabajo.
- Lo genero fuera del repo publico (carpeta local en tu maquina, no sincronizada con GitHub).
- Tu lo envias (yo no tengo tool nativa para mandar mails).
- Destinatario: me lo das tu.
- Formato propuesto: ver seccion "Formato del digest diario" al final.

## Por que

- **Floema ahora, no despues:** el frente Pollen es critico para el clímax del video (auditor multimodal en vivo). Cuanto antes empiece, mejor.
- **Equipo zigiella como cara publica:** protege identidades individuales hasta que decidamos visibilizarnos, y ya no habra que corregir 300 commits firmados con nombre real.
- **Limpieza del repo ahora, no despues:** si alguien encuentra el repo buscando "gemma 4 hackathon" y copia la tesis, pierde el proyecto ventaja narrativa. Coste bajo, beneficio alto.
- **Bitacoras internas: no tocar:** el historial honesto vale mas que la limpieza cosmetica, y el riesgo de rewrite en un repo con 3 colaboradoras activas es alto.
- **Supervision de calidad centralizada:** con 4 personas y deadline corto, un punto de review unifica criterio y evita fragmentacion.
- **Digest diario:** Bea carga con project lead + grabacion + edicion + coordinacion externa. Un resumen bien escrito al final del dia le ahorra tener que reconstruir contexto, y dejar rastro pedagogico alinea a todo el equipo extendido (quien reciba el email).

## Formato propuesto del digest diario

Correo de 1 pagina, lenguaje accesible, estructura fija:

```
Asunto: Sprout — Dia N — [titular concreto de hoy]

Hola,

Resumen de hoy en una frase:
[UNA frase clara de que movio el proyecto hoy]

Lo que avanzo:
- [bullet corto, concreto]
- [bullet corto, concreto]
- [bullet corto, concreto]

Concepto del dia:
[2-3 frases explicando UN concepto tecnico o de diseno que salio hoy,
en lenguaje para no-experta. Esto es la parte pedagogica: cada dia
quien reciba el email aprende algo nuevo.]

Lo que miramos manana:
- [1-2 cosas concretas que arrancan manana]

Bloqueos o cosas que vigilar:
- [si hay alguno; si no, se omite]

Un abrazo,
equipo zigiella
```

Tono: conversacional, sin jerga salvo si se explica, voz activa, frases cortas.

## Mecanica de ejecucion del digest

1. Cada dia al cerrar sesion de trabajo contigo, yo genero el archivo `daily_digest_YYYY-MM-DD.md` en `C:\Users\Usuario\Desktop\CAJON\digest_sprout\` (carpeta privada, fuera del repo).
2. Tu lo abres, lo copias al cliente de email, ajustas lo que quieras, y envias.
3. Cada digest lleva al final una linea `Generado por Cambium el YYYY-MM-DD HH:MM` como control.
4. Si algun dia no hay progreso real (ej. fin de semana sin actividad), el digest se omite — mejor silencio que ruido.

## Que queda pendiente

**Mio (Cambium):**
- [ ] Escribir el primer digest (el de hoy, 2026-04-16) como ejemplo para validacion de formato
- [ ] Crear carpeta `C:\Users\Usuario\Desktop\CAJON\digest_sprout\` y dejar ahi el primer digest
- [ ] `docs/20_data_contracts.md` (desbloquea a Xilema Y Floema — maxima prioridad)
- [ ] Refinar `docs/11_pollen_spec.md` con la decision de BLE-discovery + WiFi-Direct + FastAPI
- [ ] Redactar spec de onboarding de Floema paralelo al de Xilema (reaprovechando 11_pollen_spec.md)

**De Bea:**
- [ ] Dar email de destinatario del digest
- [ ] Validar formato propuesto del digest (o pedir cambios)
- [ ] Confirmar acceso de Floema al repo (collaborator GitHub)
- [ ] Confirmar compras BOM v4 tras validar flag GPIO (bitacora 2026-04-15)

**De Xilema:**
- [ ] Leer esta entrada + respuesta 6-decisiones de ayer
- [ ] Empezar bootstrap `code/rhizome/` con vertical slice en mocks
- [ ] Spike Ollama en Jetson cuando llegue hardware

**De Floema:**
- [ ] Leer onboarding Pollen + 6 decisiones
- [ ] Confirmar que los codenames le funcionan como convencion de identidad interna
- [ ] Primera entrada en bitacora (presentacion + primeras observaciones sobre Pollen spec)

## Enlaces

- [Respuesta 6 decisiones a Xilema](2026-04-15_respuesta-xilema-6-decisiones_cambium.md)
- [README publico limpio](../README.md)
- [CONTRIBUTING publico limpio](../CONTRIBUTING.md)
- [Pollen spec](../docs/11_pollen_spec.md) — onboarding de Floema
- [Rhizome spec](../docs/10_rhizome_spec.md) — onboarding de Xilema
