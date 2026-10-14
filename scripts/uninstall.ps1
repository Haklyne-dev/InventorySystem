<#
.SYNOPSIS
    InventorySystem Uninstaller
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$AppDir = "$env:LOCALAPPDATA\InventorySystem"
$BinDir = "$env:LOCALAPPDATA\Microsoft\WindowsApps"
$Launcher = "$BinDir\InventorySystem.cmd"

Write-Host "Warning: This will uninstall all application files."
Write-Host "It will NOT delete the database; all data is preserved."

$response = Read-Host "Do you want to proceed? (y/N)"
if ($response -ne 'y' -and$response -ne 'Y') {
    Write-Host "Aborted." -ForegroundColor Red
    exit 1
}

Write-Host "Uninstalling launcher..."
if (Test-Path $Launcher) {
    Remove-Item -Path $Launcher -Force -ErrorAction SilentlyContinue
}

Write-Host "Uninstalling application files..."
# Spawns a background task to delete the app directory after exit, 
# preventing file lock errors since the script runs from inside it.
Start-Process powershell.exe -ArgumentList "-WindowStyle Hidden -Command `"Start-Sleep -Seconds 1; Remove-Item -Path '$AppDir' -Recurse -Force`""

Write-Host "Finished uninstalling InventorySystem." -ForegroundColor Green