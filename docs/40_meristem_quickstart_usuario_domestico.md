# Cómo levantar Meristem en tu portátil

**Para quién es esto**: la persona que tiene Meristem instalado en su portátil doméstico (agricultor/cooperativa) y quiere usarlo cada día con su móvil Pollen.

**No necesitas saber programar**. Sí necesitas abrir una terminal y copiar un comando. La primera vez te lo dejará puesto alguien con manos en código (un voluntario, un familiar tech, un compañero de cooperativa). A partir de ahí, cada día es **un solo comando**.

---

## Parte 1 — Solo la primera vez (instalación)

Esta parte la hace **quien te ayude con el setup**, una vez. Tú lees esta sección sólo si quieres entender qué pasó.

### Qué hace falta en el portátil

- **Sistema operativo**: Windows 10/11, macOS o Linux. Cualquiera vale.
- **RAM**: mínimo **8 GB** para uso normal. Recomendado **16 GB** si quieres que Meristem use el modelo de IA grande (Gemma 4 E4B).
- **Disco**: ~6 GB libres (el modelo de IA pesa ~5 GB; el resto del software, ~500 MB).
- **Python 3.13** instalado.
- **Red Wi-Fi doméstica**: el portátil y el móvil tienen que estar en la **misma red Wi-Fi**.

### Pasos del setup inicial

1. Clonar el repositorio del proyecto Sprout en el portátil (carpeta `T6-GEMMA`).
2. Entrar a `code/meristem_node/` e instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Descargar el modelo `gemma-4-E4B-it-Q4_K_M.gguf` (~5 GB) y dejarlo en `T6-GEMMA/models/`. Esto **solo si vais a usar el modo IA real** (ver Parte 3).
4. Comprobar que todo carga:
   ```bash
   cd code/meristem_node
   python -m pytest tests/ -q
   ```
   Debe terminar con algo como `100+ passed`. Si falla, hay algo mal instalado.

A partir de aquí, todos los días sólo usas la Parte 2.

---

## Parte 2 — Cada día (uso normal)

### Paso 1 — Abre una terminal

- **Windows**: busca "Símbolo del sistema" o "PowerShell" en el menú inicio.
- **Mac**: Spotlight (`Cmd+Espacio`) → escribe "Terminal".
- **Linux**: ya sabes.

### Paso 2 — Ve a la carpeta del proyecto

```bash
cd C:\DATA\PETS\TEST\T6-GEMMA\code\meristem_node
```

*(Ajusta la ruta a donde está tu carpeta del proyecto.)*

### Paso 3 — Enciende Meristem

**Modo recomendado (rápido, sin esperas)**:

En Windows (PowerShell):
```powershell
$env:MERISTEM_USE_LLM = "false"
python -m src.main
```

En macOS / Linux:
```bash
MERISTEM_USE_LLM=false python -m src.main
```

Verás algo así:
```
INFO:     Started server process
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:13000
```

Eso significa que **Meristem está vivo**. Deja esa ventana abierta — si la cierras, se apaga Meristem.

### Paso 4 — Abre la pantalla de Meristem

En tu navegador (Firefox, Chrome, Edge), entra a:

```
http://localhost:13000/ui/
```

Verás una pantalla en castellano con cinco zonas (tu parcela hoy, sincronización con Pollen, eventos, visitas recibidas, políticas emitidas). Al principio están vacías — es normal hasta que Pollen llegue con datos.

### Paso 5 — Conecta tu móvil Pollen

1. Coge el móvil. Comprueba que está conectado a la **misma Wi-Fi** que el portátil.
2. Abre la app **Pollen**.
3. Toca **"Conectar a Meristem"**.

En menos de 2 segundos debes ver:

- En el móvil: confirmación "conectado a Meristem".
- En la pantalla del portátil (la del navegador): el círculo arriba a la derecha pasa de gris a **verde**.

### Paso 6 — Usa Pollen como siempre

Desde el móvil:

- **"Cargar política actualizada"** → tu móvil descarga la última política que Meristem tiene guardada.
- **"Descargar datos de campo"** → tu móvil entrega a Meristem todo lo que recogiste hoy de tus parcelas, y Meristem te devuelve una política nueva ajustada.

En la pantalla del portátil verás cómo se llenan las tablas con las visitas recibidas y las políticas emitidas. La tarjeta "Tu parcela hoy" se actualiza con el estado más reciente.

### Paso 7 — Cuando termines

1. Cierra la app Pollen en el móvil (o presiona "Desconectar" si la app lo ofrece).
2. En la ventana de la terminal del portátil, pulsa `Ctrl+C` para apagar Meristem.
3. Listo. Puedes cerrar la terminal.

---

## Si algo no funciona

### El móvil dice "no encuentro Meristem"

Posibles causas y soluciones, en orden:

1. **¿Están el móvil y el portátil en la misma Wi-Fi?** Comprueba el nombre de la red en ambos. Si tienes Wi-Fi de doble banda (2.4 GHz y 5 GHz), a veces se separan — usa la misma.
2. **¿Está Meristem encendido?** En el navegador del portátil entra a `http://localhost:13000/health`. Si ves un JSON con `"status":"ok"`, está vivo. Si no, vuelve a la Parte 2 Paso 3.
3. **El descubrimiento automático falló**. En Pollen, en la opción "conectar manualmente", introduce la dirección IP del portátil. Para saber tu IP:
   - Windows: en la terminal escribe `ipconfig` y busca "Dirección IPv4".
   - Mac/Linux: `ifconfig` o `ip addr`.
   - Será algo como `192.168.1.36`. En Pollen pones: `http://192.168.1.36:13000`.

### La pantalla del navegador no se actualiza

- Pulsa `Ctrl+F5` para refrescar sin caché.
- Comprueba que ves `http://localhost:13000/ui/` (con la `/ui/` al final).

### Meristem se cierra solo / la terminal muestra "Error"

- Probablemente otra cosa en tu portátil ya estaba usando el puerto 13000. Reinicia el portátil y vuelve a intentar.
- Si pasa de nuevo, contacta a tu voluntario tech y dile que mire el mensaje exacto de error.

### El portátil va lento mientras Meristem está encendido

- En **modo rápido** (el del Paso 3), Meristem consume muy poca RAM y CPU. Si va lento, mira si hay otras apps abiertas (navegador con muchas pestañas, edición de video, etc.).
- Si quisiste usar el **modo IA completo** (ver Parte 3), ese sí consume bastante. Cierra otras apps grandes mientras lo uses.

---

## Parte 3 — Modo IA completo (opcional, lento)

Esta parte es para cuando quieras que Meristem te dé **explicaciones más elaboradas en castellano natural** sobre lo que ve. Por ejemplo, después de un día con alertas, puedes pedirle que te cuente qué pasó y por qué.

**Aviso honesto**:

- Cada respuesta tarda **entre 1 y 3 minutos** (Meristem está pensando en local con tu portátil; no es Google).
- Necesitas **al menos 6 GB de RAM libre**.
- Tienes que cerrar otras apps pesadas mientras tanto (navegador con muchas pestañas, herramientas grandes).

### Cómo encender el modo IA

En lugar del comando del Paso 3, usas tres ventanas distintas (suena más complicado de lo que es; tu voluntario tech te lo deja preparado en un script una vez).

Windows (PowerShell):
```powershell
# Ventana 1 — el motor de IA
cd C:\DATA\PETS\TEST\T6-GEMMA
.\tools\llama.cpp\llama-server.exe -m models\gemma-4-E4B-it-Q4_K_M.gguf --host 0.0.0.0 --port 8080 -c 4096 --jinja

# Ventana 2 — el adaptador (espera 1 minuto a que la ventana 1 diga "ready")
cd C:\DATA\PETS\TEST\T6-GEMMA\code\meristem_inference_adapter
$env:MERISTEM_ADAPTER_PORT = "11435"
python -m src.main

# Ventana 3 — Meristem (espera a que la ventana 2 esté listo)
cd C:\DATA\PETS\TEST\T6-GEMMA\code\meristem_node
$env:MERISTEM_USE_LLM = "true"
$env:MERISTEM_ADAPTER_URL = "http://localhost:11435"
python -m src.main
```

A partir de ahí, lo mismo: abres `http://localhost:13000/ui/`, conectas el móvil, y usas Pollen igual. La diferencia: ahora cada respuesta tarda más pero está redactada por la IA local.

### Para apagar

`Ctrl+C` en las tres ventanas (orden inverso: Meristem, adaptador, motor IA). Ciérralas.

---

## Preguntas frecuentes

### ¿Mis datos salen de mi casa?

**No**. Todo corre en tu portátil. Meristem no envía nada a internet. La IA, si la usas, tampoco — está descargada en tu disco y razona localmente. La única "red" que se usa es tu Wi-Fi doméstica entre el portátil y tu móvil.

### ¿Funciona sin internet?

**Sí**. Solo necesitas Wi-Fi local (para que móvil y portátil se vean). No hace falta que esa Wi-Fi tenga conexión a internet.

### ¿Por qué tengo que dejar la terminal abierta?

Porque Meristem corre dentro de esa terminal. Si la cierras, lo apagas. Más adelante haremos un atajo para que arranque "en segundo plano" sin verlo, pero de momento es lo que hay.

### ¿Puedo tener el portátil cerrado mientras voy al campo?

Sí, pero Meristem se apaga al cerrar la tapa (o entrar el portátil en suspensión). Cuando vuelvas, lo enciendes de nuevo con un comando. **Tus datos no se pierden** — quedan guardados en disco.

### ¿Y si cambio de portátil?

Lleva contigo la carpeta `T6-GEMMA` entera (en USB o disco externo). En el nuevo portátil, la copias y haces el setup de la Parte 1 una vez. Tus históricos viajan dentro.

---

## Resumen del día normal

```
1. Abre terminal
2. cd a code/meristem_node
3. Ejecuta el comando del Paso 3
4. Abre http://localhost:13000/ui/ en el navegador
5. Coge el móvil, abre Pollen, conecta
6. Usa Pollen como siempre
7. Al final, Ctrl+C en la terminal
```

Eso es todo. Si llevas una semana usándolo y sientes que algo va raro, llama a tu voluntario tech con calma. Meristem está diseñado para no romperse, pero las redes Wi-Fi domésticas son lo que son.

— Meristem (slow brain doméstico, Sprout)
