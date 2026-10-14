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

$response = Read-Host "Do you want to proceed? (y/N): "
if ($response -ne 'y' -and$response -ne 'Y') {
    Write-Host "Aborted." -ForegroundColor Red
    exit 1
}

Write-Host "Scheduling complete cleanup..."

$cleanupScript = "Start-Sleep -Seconds 2; Remove-Item -Path '$AppDir' -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path '$Launcher' -Force -ErrorAction SilentlyContinue"
Start-Process powershell.exe -ArgumentList "-WindowStyle Hidden -Command `"$cleanupScript`""

Write-Host "Finished uninstalling InventorySystem." -ForegroundColor Green