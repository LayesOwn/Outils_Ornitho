# Crée un raccourci ORNI-LAB sur le bureau
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$batFile    = Join-Path $projectDir "ORNI-LAB.bat"
$desktop    = [Environment]::GetFolderPath("Desktop")
$shortcut   = Join-Path $desktop "ORNI-LAB.lnk"

$wsh  = New-Object -ComObject WScript.Shell
$link = $wsh.CreateShortcut($shortcut)
$link.TargetPath       = $batFile
$link.WorkingDirectory = $projectDir
$link.Description      = "ORNI-LAB — Laboratoire de Modélisation Ornithologique"
$link.WindowStyle      = 1

# Icône Python si disponible, sinon icône cmd
$pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if ($pythonExe) {
    $link.IconLocation = "$pythonExe,0"
}

$link.Save()

Write-Host ""
Write-Host "  Raccourci ORNI-LAB créé sur le bureau !" -ForegroundColor Green
Write-Host "  Chemin : $shortcut" -ForegroundColor Cyan
Write-Host ""
