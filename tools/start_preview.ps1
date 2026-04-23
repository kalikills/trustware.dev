[CmdletBinding()]
param(
  [int]$Port = 15000,
  [string]$Bind = "127.0.0.1",
  [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"

$siteRoot = Split-Path -Parent $PSScriptRoot
$previewServer = Join-Path $PSScriptRoot "preview_server.py"

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue

if ($pythonCommand) {
  $pythonExe = $pythonCommand.Source
  $pythonArgs = @(
    $previewServer,
    "--port", $Port.ToString(),
    "--bind", $Bind,
    "--directory", $siteRoot
  )
}
elseif ($pythonLauncher) {
  $pythonExe = $pythonLauncher.Source
  $pythonArgs = @(
    "-3",
    $previewServer,
    "--port", $Port.ToString(),
    "--bind", $Bind,
    "--directory", $siteRoot
  )
}
else {
  throw "Python was not found in PATH. Install Python or add it to PATH, then run this script again."
}

$previewUrl = "http://{0}:{1}/" -f $Bind, $Port

Write-Host ("Serving Trustware preview from: {0}" -f $siteRoot) -ForegroundColor Cyan
Write-Host ("Preview URL: {0}" -f $previewUrl) -ForegroundColor Cyan

if (-not $NoBrowser) {
  Start-Process $previewUrl
}

& $pythonExe @pythonArgs
