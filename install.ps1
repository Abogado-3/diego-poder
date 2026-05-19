# Instalador de DIEGO para Windows.
# Uso (en PowerShell):
#   iwr https://raw.githubusercontent.com/Abogado-3/diego-poder/main/install.ps1 -UseBasicParsing | iex

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=============================================="
Write-Host "  DIEGO - Instalador para Windows"
Write-Host "=============================================="
Write-Host ""

$Repo = "Abogado-3/diego-poder"
$InstallDir = Join-Path $HOME ".claude\diego-poder"

# --- 1. Verificar Python ---
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-Host "ERROR: Python no esta instalado." -ForegroundColor Red
    Write-Host "   Instalalo desde https://www.python.org/downloads/windows/"
    Write-Host "   Marca 'Add Python to PATH' al instalarlo."
    exit 1
}
$pyExe = $python.Source
Write-Host "OK Python encontrado: $(& $pyExe --version)" -ForegroundColor Green

# --- 2. Instalar dependencias ---
Write-Host ""
Write-Host "-> Instalando librerias (reportlab, openpyxl)..."
& $pyExe -m pip install --user --quiet reportlab openpyxl
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: fallo pip install." -ForegroundColor Red
    exit 1
}
Write-Host "OK Librerias instaladas." -ForegroundColor Green

# --- 3. Descargar repo ---
Write-Host ""
Write-Host "-> Descargando DIEGO desde GitHub..."
$tmpDir = Join-Path $env:TEMP "diego-poder-install-$(Get-Random)"
New-Item -ItemType Directory -Path $tmpDir | Out-Null

$zipPath = Join-Path $tmpDir "main.zip"
Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/$Repo/archive/refs/heads/main.zip" -OutFile $zipPath
Expand-Archive -Path $zipPath -DestinationPath $tmpDir -Force
$repoDir = Join-Path $tmpDir "diego-poder-main"

if (-not (Test-Path $repoDir)) {
    Write-Host "ERROR: no pude descargar el repo." -ForegroundColor Red
    exit 1
}
Write-Host "OK Codigo descargado." -ForegroundColor Green

# --- 4. Copiar archivos ---
Write-Host ""
Write-Host "-> Instalando archivos en $InstallDir..."
$agentsDir = Join-Path $HOME ".claude\agents"
$scriptsDir = Join-Path $InstallDir "scripts"
$tmplDir = Join-Path $InstallDir "scheduled-task-template"

New-Item -ItemType Directory -Path $agentsDir -Force | Out-Null
New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null
New-Item -ItemType Directory -Path $tmplDir -Force | Out-Null

Copy-Item -Path (Join-Path $repoDir "agents\diego.md") -Destination $agentsDir -Force
Copy-Item -Path (Join-Path $repoDir "scripts\*") -Destination $scriptsDir -Recurse -Force
Copy-Item -Path (Join-Path $repoDir "scheduled-task-template\briefing-prompt.md") -Destination $tmplDir -Force
Write-Host "OK Archivos copiados." -ForegroundColor Green

# --- 5. Autodetectar OneDrive ---
Write-Host ""
Write-Host "-> Buscando el OneDrive del firm..."
$detectedJson = & $pyExe (Join-Path $scriptsDir "diego_paths.py") --autodetect 2>$null
$detected = ""
try {
    $detected = ($detectedJson | ConvertFrom-Json).detected
} catch {
    $detected = ""
}

$firmPath = ""
if ($detected) {
    Write-Host "OK OneDrive detectado:" -ForegroundColor Green
    Write-Host "   $detected"
    $resp = Read-Host "Es correcto? [Y/n]"
    if ($resp -eq "" -or $resp -eq "Y" -or $resp -eq "y") {
        $firmPath = $detected
    }
}

if (-not $firmPath) {
    Write-Host ""
    Write-Host "Pega la ruta absoluta donde tienes sincronizado 'ABOGADO01 - ARCHIVO DIGITAL CAVV'."
    $firmPath = Read-Host "Ruta"
}

if (-not (Test-Path $firmPath)) {
    Write-Host "ERROR: la ruta no existe." -ForegroundColor Red
    Remove-Item -Recurse -Force $tmpDir
    exit 1
}

# --- 6. Carpeta compartida ---
$diegoSharedDir = Join-Path $firmPath "0. DIEGO - Sustitución de Poder"
if (-not (Test-Path $diegoSharedDir)) {
    Write-Host ""
    Write-Host "ADVERTENCIA: la carpeta compartida '0. DIEGO - Sustitucion de Poder' no existe en el OneDrive del firm." -ForegroundColor Yellow
    Write-Host "   El primer abogado del firm que instale DIEGO debe crearla."
    Write-Host "   Por ahora guardo la config local pero DIEGO no podra generar PDFs hasta que exista esa carpeta."
}

# --- 7. Config local del usuario ---
$cfgDir = Join-Path $env:APPDATA "diego-poder"
New-Item -ItemType Directory -Path $cfgDir -Force | Out-Null
$cfgPath = Join-Path $cfgDir "config.json"
$cfgJson = @{ firm_path = $firmPath } | ConvertTo-Json
Set-Content -Path $cfgPath -Value $cfgJson -Encoding UTF8

Write-Host ""
Write-Host "OK Config local guardada en $cfgPath" -ForegroundColor Green

# --- 8. Verificacion ---
Write-Host ""
Write-Host "-> Verificando instalacion..."
& $pyExe (Join-Path $scriptsDir "diego_paths.py") --show

# Cleanup
Remove-Item -Recurse -Force $tmpDir

Write-Host ""
Write-Host "=============================================="
Write-Host "  OK DIEGO instalado correctamente" -ForegroundColor Green
Write-Host "=============================================="
Write-Host ""
Write-Host "Proximos pasos:"
Write-Host ""
Write-Host "1. Abre Claude Code y di:  Diego, hola"
Write-Host "2. Para el briefing diario: Diego, configura mi briefing diario"
Write-Host "3. Para una sustitucion:   Diego, prepara una sustitucion de poder para ..."
Write-Host ""
