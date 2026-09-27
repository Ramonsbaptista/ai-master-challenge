$ErrorActionPreference = "Stop"
$Utf8 = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = $Utf8
[Console]::OutputEncoding = $Utf8
$OutputEncoding = $Utf8
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
function Stop-WithDiagnostic([string]$Cause, [string]$Fix, [string]$Diagnostic) {
  Write-Host "Causa: $Cause"
  Write-Host "Como corrigir: $Fix"
  Write-Host "Diagnóstico: $Diagnostic"
  exit 1
}
try { $Version = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null } catch { $Version = $null }
if (-not $Version -or [version]$Version -lt [version]"3.11" -or [version]$Version -ge [version]"3.15") {
  Stop-WithDiagnostic "Python 3.11 a 3.14 não foi encontrado." "Instale uma versão suportada em https://www.python.org/downloads/ ou use o notebook Colab incluído." "Versão detectada: $Version"
}
$Venv = Join-Path $Root ".venv"
$VenvExisted = Test-Path $Venv
$VenvPython = Join-Path $Venv "Scripts\python.exe"
$VenvHealthy = $false
if ($VenvExisted -and (Test-Path $VenvPython -PathType Leaf)) {
  try {
    & $VenvPython -c "import sys" 2>$null
    if ($LASTEXITCODE -eq 0) {
      & $VenvPython -m pip --version >$null 2>&1
      $VenvHealthy = $LASTEXITCODE -eq 0
    }
  } catch { $VenvHealthy = $false }
}
if ($VenvExisted -and -not $VenvHealthy) {
  Write-Host "Ambiente virtual incompleto; recriando .venv."
  Remove-Item -LiteralPath $Venv -Recurse -Force
  $VenvExisted = $false
}
if (-not $VenvExisted) {
  & python -m venv $Venv
  if ($LASTEXITCODE -ne 0) { Stop-WithDiagnostic "Não foi possível criar o ambiente virtual." "Verifique permissão de escrita na pasta da solução ou use o notebook Colab." "python -m venv retornou código $LASTEXITCODE." }
}
& $VenvPython -m pip --version >$null
if ($LASTEXITCODE -ne 0) { Stop-WithDiagnostic "O ambiente virtual foi criado sem pip." "Reinstale o Python com o componente pip/ensurepip ou use o notebook Colab." "python -m pip --version retornou código $LASTEXITCODE." }
& $VenvPython -m pip install -r "$Root\requirements.txt"
if ($LASTEXITCODE -ne 0 -and $VenvHealthy) {
  Write-Host "Ambiente virtual incompleto; recriando .venv."
  Remove-Item -LiteralPath $Venv -Recurse -Force
  & python -m venv $Venv
  if ($LASTEXITCODE -eq 0) { & $VenvPython -m pip install -r "$Root\requirements.txt" }
}
if ($LASTEXITCODE -ne 0) { Stop-WithDiagnostic "As dependências não puderam ser instaladas." "Verifique a conexão e tente novamente, ou use o notebook Colab." "pip retornou código $LASTEXITCODE." }
$env:PYTHONPATH = Join-Path $Root "src"
if ($args -contains "--cli") {
  & $VenvPython -m ticket_classifier.cli
} else {
  & $VenvPython -m ticket_classifier.web
}
if ($LASTEXITCODE -ne 0) { Stop-WithDiagnostic "A aplicação terminou com erro." "Restaure os artefatos e dados da solução e tente novamente." "Aplicação retornou código $LASTEXITCODE." }
