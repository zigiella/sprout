# run_pending.ps1
# Lanza adapter + Phase 1.5 + Phase 3 + analisis en una sola ejecucion.
# Pensado para correr "a pelo": Ollama arrancado y nada mas.
#
# === ANTES DE EJECUTAR (importante para liberar memoria) ===
#   1. Cierra Claude Code (la app y/o la terminal donde corra). Imprescindible.
#   2. Cierra Chrome / Edge / Firefox con muchas pestanyas.
#   3. Cierra VS Code u otros editores pesados.
#   4. Cualquier app de chat/video (Slack, Discord, Zoom).
#   5. Comprueba en Ctrl+Shift+Esc -> "Memoria" que tienes >=6 GB libres.
#      Con menos de 4 GB, los runs de Phase 3 (multi-turn) arriesgan OOM.
#
# Pre-requisitos tecnicos:
#   - Ollama en http://localhost:11434 con gemma4:e4b descargado
#   - PowerShell 7+ (pwsh) en PATH
#   - python en PATH con dependencias del adapter y del harness instaladas
#   - cwd = raiz del repo (C:\DATA\PETS\TEST\T6-GEMMA)
#
# Uso:
#   pwsh -File code\tuning\run_pending.ps1
#
# Que hace, paso a paso:
#   1. Pre-flight: comprueba memoria libre, Ollama up, gemma4:e4b presente
#   2. Arranca el adapter en :12000 en background, log a adapter.log
#   3. Smoke test (1 prompt) para confirmar el path completo y precalentar
#      el modelo en RAM (la primera carga tarda ~30s)
#   4. Phase 1.5  (16 runs EN/ES)  con --resume      -> log: phase1_5.console.log
#   5. Phase 3    (12 runs KV)     con --resume      -> log: phase3.console.log
#   6. analyze.py (resumen impreso y archivado)      -> log: analyze.console.log
#   7. Para el adapter (siempre, incluso si algun paso falla)
#
# Estimacion de duracion (orientativa):
#   - Smoke:     30-60s
#   - Phase 1.5: 60-90 min (16 runs, num_predict alto en algunas configs)
#   - Phase 3:   45-75 min (12 runs multi-turn, mas pesados por warmup)
#   - Analyze:   <5s
#   Total: ~2-3h. Puedes dejarlo corriendo y volver.
#
# --resume es seguro: dedupea por run_id, prefiere ultimo OK. Si Phase 1.5
# o Phase 3 ya tuvieran runs OK previos, se respetan y solo se rellenan
# los que falten.

$ErrorActionPreference = 'Stop'
$repo = 'C:\DATA\PETS\TEST\T6-GEMMA'
Set-Location $repo

$global_start = Get-Date

function Write-Section($msg) {
    $ts = (Get-Date).ToString('HH:mm:ss')
    $elapsed = ((Get-Date) - $global_start).ToString('hh\:mm\:ss')
    Write-Host ''
    Write-Host "== [$ts | +$elapsed]  $msg ==" -ForegroundColor Cyan
}

Write-Section 'Pre-flight'

# 1. Memoria libre
$os = Get-CimInstance Win32_OperatingSystem
$free_gb  = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$total_gb = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
Write-Host ("  Memoria libre: {0} GB / {1} GB total" -f $free_gb, $total_gb)
if ($free_gb -lt 4) {
    Write-Host '  AVISO: < 4 GB libres. Phase 3 puede tocar OOM. Considera cerrar mas apps y reintentar.' -ForegroundColor Yellow
} elseif ($free_gb -lt 6) {
    Write-Host '  AVISO: < 6 GB libres. Margen estrecho pero deberia funcionar.' -ForegroundColor Yellow
} else {
    Write-Host '  Memoria OK.' -ForegroundColor Green
}

# 2. Ollama up + gemma4:e4b presente
try {
    $tags = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 5
    Write-Host "  Ollama OK  (modelos cargables: $($tags.models.Count))"
} catch {
    Write-Error 'Ollama no responde en :11434. Arranca `ollama serve` y vuelve a lanzar.'
    exit 1
}

$has_gemma = $tags.models | Where-Object { $_.name -like 'gemma4:e4b*' }
if (-not $has_gemma) {
    Write-Error 'gemma4:e4b no esta descargado. `ollama pull gemma4:e4b` antes de seguir.'
    exit 1
}
Write-Host '  gemma4:e4b OK'

# 3. Aviso explicito sobre Claude
Write-Host '  Claude: si lo tienes abierto, este script va a chocar con el por memoria.'
Write-Host '          Cierra Claude ahora si no lo has hecho. Continuo en 5s (Ctrl+C para abortar).'
Start-Sleep -Seconds 5

# 4. Arrancar adapter en :12000
$env:INFERENCE_BACKEND     = 'local'
$env:ADAPTER_PORT          = '12000'
$env:OLLAMA_UPSTREAM_HOST  = 'http://localhost:11434'

$results_dir = Join-Path $repo 'code\tuning\results'
if (-not (Test-Path $results_dir)) { New-Item -ItemType Directory -Path $results_dir | Out-Null }
$adapter_log     = Join-Path $results_dir 'adapter.log'
$adapter_log_err = Join-Path $results_dir 'adapter.err.log'
$smoke_log       = Join-Path $results_dir 'smoke.console.log'
$p15_log         = Join-Path $results_dir 'phase1_5.console.log'
$p3_log          = Join-Path $results_dir 'phase3.console.log'
$analyze_log     = Join-Path $results_dir 'analyze.console.log'

Write-Section 'Arrancando adapter en :12000'
# Nota: usamos -NoNewWindow + redireccion de stdio. El patron alternativo
# (-WindowStyle Hidden + redireccion) lo bloquea AMSI/Defender por similitud
# con loaders sigilosos. Mismo efecto practico: el adapter corre en background
# sin ventana propia, sus logs van a $adapter_log / $adapter_log_err.
$adapter = Start-Process -FilePath 'python' `
    -ArgumentList '-m','src.main' `
    -WorkingDirectory (Join-Path $repo 'code\meristem_inference_adapter') `
    -RedirectStandardOutput $adapter_log `
    -RedirectStandardError  $adapter_log_err `
    -PassThru -NoNewWindow

# Esperar hasta 30s a que /api/tags responda
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        $r = Invoke-WebRequest -Uri 'http://localhost:12000/api/tags' -TimeoutSec 2 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch { }
}
if (-not $ready) {
    Write-Host "  Adapter no respondio en 30s. Mira $adapter_log y $adapter_log_err" -ForegroundColor Red
    Stop-Process -Id $adapter.Id -Force -ErrorAction SilentlyContinue
    exit 1
}
Write-Host "  Adapter OK en :12000  (PID $($adapter.Id))"
Write-Host "  Log adapter: $adapter_log"

$exit_code = 0
try {
    Write-Section 'Smoke test (1 prompt via adapter, precalienta modelo)'
    & python code\tuning\harness.py --smoke --adapter-url http://localhost:12000 2>&1 |
        Tee-Object -FilePath $smoke_log
    if ($LASTEXITCODE -ne 0) { throw 'smoke fallo' }

    Write-Section 'Phase 1.5 - 16 runs EN/ES (estimado 60-90 min)'
    Write-Host "  Log: $p15_log"
    Write-Host '  Veras lineas tipo "[3/16] PI01_C2_balanced_es (lang=es)" segun avance.'
    & python code\tuning\harness.py --matrix code\tuning\matrix_phase1_5.yaml --adapter-url http://localhost:12000 --resume 2>&1 |
        Tee-Object -FilePath $p15_log
    if ($LASTEXITCODE -ne 0) { throw 'phase 1.5 fallo' }

    Write-Section 'Phase 3 - 12 runs multi-turn KV (estimado 45-75 min)'
    Write-Host "  Log: $p3_log"
    Write-Host '  Veras lineas tipo "[5/12] phase3_audit_visit_D3_T_ON_HIGH_CTX" segun avance.'
    & python code\tuning\harness.py --matrix code\tuning\matrix_phase3.yaml --adapter-url http://localhost:12000 --resume 2>&1 |
        Tee-Object -FilePath $p3_log
    if ($LASTEXITCODE -ne 0) { throw 'phase 3 fallo' }

    Write-Section 'Resumen final (analyze.py)'
    & python code\tuning\analyze.py 2>&1 | Tee-Object -FilePath $analyze_log
} catch {
    Write-Host "FALLO: $_" -ForegroundColor Red
    $exit_code = 1
} finally {
    Write-Section 'Parando adapter'
    Stop-Process -Id $adapter.Id -Force -ErrorAction SilentlyContinue
    Write-Host '  Adapter detenido.'
}

$total_elapsed = ((Get-Date) - $global_start).ToString('hh\:mm\:ss')
Write-Host ''
if ($exit_code -eq 0) {
    Write-Host "TODO OK.  Tiempo total: $total_elapsed" -ForegroundColor Green
    Write-Host ''
    Write-Host 'Datos crudos:'
    Write-Host "  - $results_dir\phase1_5.jsonl"
    Write-Host "  - $results_dir\phase3.jsonl"
    Write-Host 'Logs de consola (para que Meristem los lea cuando vuelva):'
    Write-Host "  - $smoke_log"
    Write-Host "  - $p15_log"
    Write-Host "  - $p3_log"
    Write-Host "  - $analyze_log"
    Write-Host "  - $adapter_log"
} else {
    Write-Host "TERMINADO CON ERROR.  Tiempo total: $total_elapsed" -ForegroundColor Red
    Write-Host "Mira logs en $results_dir\"
}
exit $exit_code
