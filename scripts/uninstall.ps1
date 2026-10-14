$ErrorActionPreference = "Stop"

$AppDir  = "$env:LOCALAPPDATA\InventorySystem"
$BinDir  = "$env:LOCALAPPDATA\Microsoft\WindowsApps"

Write-Host "Warning: This will uninstall all aplication files"
Write-Host "It will NOT delete the database, all data is preserved"

$response = Read-Host "Do you want to proceed? (y/N)"
        if ($response -ne 'y' -and $response -ne 'Y') {
            Write-Host "Aborted." -ForegroundColor Red
            exit 1
        }

Write-Host "Uninstalling $APP_DIR..."
rm -r "$APP_DIR"

Write-Host "Uninstalling Launcher[$BinDir/InventorySystem.cmd]..."
rm -r "$BIN_DIR/InventorySystem.cmd"

Write-Host "Finished uninstalling InventorySystem"