# run_pending.ps1
# Lanza adapter + Phase 1.5 + Phase 3 + analisis en una sola ejecucion.
# Pensado para correr "a pelo": Ollama arrancado y nada mas.
#
# Pre-requisitos:
#   - Ollama en http://localhost:11434 con gemma4:e4b descargado
#   - PowerShell 7+ (pwsh) en PATH
#   - python en PATH con dependencias del adapter y del harness instaladas
#   - cwd = raiz del repo (C:\DATA\PETS\TEST\T6-GEMMA)
#
# Uso:
#   pwsh -File code\tuning\run_pending.ps1
#
# Que hace:
#   1. Verifica Ollama up y gemma4:e4b presente
#   2. Arranca el adapter en :12000 en background, redirigiendo log
#   3. Smoke test (1 prompt) para confirmar el path completo
#   4. Phase 1.5  (16 runs EN/ES)  con --resume
#   5. Phase 3    (12 runs KV)     con --resume
#   6. analyze.py (resumen impreso)
#   7. Para el adapter (siempre, incluso si algun paso falla)
#
# --resume es seguro: dedupea por run_id, prefiere ultimo OK. Si Phase 1.5
# o Phase 3 ya tuvieran runs OK previos, se respetan y solo se rellenan
# los que falten.

$ErrorActionPreference = 'Stop'
$repo = 'C:\DATA\PETS\TEST\T6-GEMMA'
Set-Location $repo

function Write-Section($msg) {
    Write-Host ''
    Write-Host "== $msg ==" -ForegroundColor Cyan
}

Write-Section 'Pre-flight'

# 1. Ollama up + gemma4:e4b presente
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

# 2. Arrancar adapter en :12000
$env:INFERENCE_BACKEND     = 'local'
$env:ADAPTER_PORT          = '12000'
$env:OLLAMA_UPSTREAM_HOST  = 'http://localhost:11434'

$results_dir = Join-Path $repo 'code\tuning\results'
if (-not (Test-Path $results_dir)) { New-Item -ItemType Directory -Path $results_dir | Out-Null }
$adapter_log     = Join-Path $results_dir 'adapter.log'
$adapter_log_err = Join-Path $results_dir 'adapter.err.log'

Write-Section 'Arrancando adapter en :12000'
$adapter = Start-Process -FilePath 'python' `
    -ArgumentList '-m','src.main' `
    -WorkingDirectory (Join-Path $repo 'code\meristem_inference_adapter') `
    -RedirectStandardOutput $adapter_log `
    -RedirectStandardError  $adapter_log_err `
    -PassThru -WindowStyle Hidden

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

$exit_code = 0
try {
    Write-Section 'Smoke test (1 prompt via adapter)'
    & python code\tuning\harness.py --smoke --adapter-url http://localhost:12000
    if ($LASTEXITCODE -ne 0) { throw 'smoke fallo' }

    Write-Section 'Phase 1.5 - 16 runs EN/ES'
    & python code\tuning\harness.py --matrix code\tuning\matrix_phase1_5.yaml --adapter-url http://localhost:12000 --resume
    if ($LASTEXITCODE -ne 0) { throw 'phase 1.5 fallo' }

    Write-Section 'Phase 3 - 12 runs multi-turn KV'
    & python code\tuning\harness.py --matrix code\tuning\matrix_phase3.yaml --adapter-url http://localhost:12000 --resume
    if ($LASTEXITCODE -ne 0) { throw 'phase 3 fallo' }

    Write-Section 'Resumen (analyze.py)'
    & python code\tuning\analyze.py
} catch {
    Write-Host "FALLO: $_" -ForegroundColor Red
    $exit_code = 1
} finally {
    Write-Section 'Parando adapter'
    Stop-Process -Id $adapter.Id -Force -ErrorAction SilentlyContinue
    Write-Host '  Listo.'
}

if ($exit_code -eq 0) {
    Write-Host ''
    Write-Host 'TODO OK.' -ForegroundColor Green
} else {
    Write-Host ''
    Write-Host 'TERMINADO CON ERROR. Mira logs en code\tuning\results\.' -ForegroundColor Red
}
exit $exit_code
