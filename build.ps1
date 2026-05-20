$ErrorActionPreference = "Stop"

function Assert-Success {
    param(
        [string]$StepName
    )

    if ($LASTEXITCODE -ne 0) {
        throw "Fallo durante: $StepName"
    }
}

Write-Host "Preparando herramientas locales de compilacion..." -ForegroundColor Cyan
$toolsDir = ".build-tools"
$resolvedToolsDir = Join-Path (Get-Location) $toolsDir

if (Test-Path ".venv") {
    Write-Host "Se detecto un entorno virtual previo incompleto. Se eliminara..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".venv"
}

if (-not (Test-Path $toolsDir)) {
    New-Item -ItemType Directory -Path $toolsDir | Out-Null
}

Write-Host "Instalando dependencias..." -ForegroundColor Cyan
python -m pip install --upgrade pip
Assert-Success "actualizar pip"

python -m pip install --upgrade --target $toolsDir -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "No se pudieron descargar dependencias. Se comprobara si ya existen en Python local..." -ForegroundColor Yellow
    @'
import importlib
modules = ["PyInstaller", "reportlab", "PIL"]
missing = []
for module in modules:
    try:
        importlib.import_module(module)
    except Exception:
        missing.append(module)
if missing:
    raise SystemExit(f"Faltan modulos: {', '.join(missing)}")
print("Dependencias globales disponibles.")
'@ | python -
    Assert-Success "validar dependencias globales"
}

$env:PYTHONPATH = $resolvedToolsDir

$addDataArgs = @("--add-data", "assets;assets")
if (Test-Path "github_token.txt") {
    Write-Host "Incluyendo github_token.txt dentro del .exe..." -ForegroundColor Cyan
    $addDataArgs += @("--add-data", "github_token.txt;.")
}

Write-Host "Generando el .exe..." -ForegroundColor Cyan
python -m PyInstaller --noconfirm --onefile --windowed @addDataArgs --icon "assets\app_icon.ico" --name "Richiesta_di_approvvigionamento" app.py
Assert-Success "generar el ejecutable"

Write-Host "Compilacion completada. Revisa dist\Richiesta_di_approvvigionamento.exe" -ForegroundColor Green
