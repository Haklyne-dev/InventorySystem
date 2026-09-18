$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/Haklyne-dev/InventorySystem.git"
$AppDir  = "$env:LOCALAPPDATA\InventorySystem"
$BinDir  = "$env:LOCALAPPDATA\Microsoft\WindowsApps"

New-Item -ItemType Directory -Force -Path $AppDir | Out-Null

if (Test-Path "$AppDir\repo\.git") {
    git -C "$AppDir\repo" fetch --tags --quiet
} else {
    git clone $RepoUrl "$AppDir\repo"
}

$LatestTag = git -C "$AppDir\repo" tag --sort=-v:refname | Select-Object -First 1
git -C "$AppDir\repo" checkout $LatestTag

python -m venv "$AppDir\venv"
Write-Progress -Activity "Installing Python Packages" -Status "Running pip install..." -PercentComplete -1
& "$AppDir\venv\Scripts\python.exe" -m pip install -r "$AppDir\repo\requirements.txt" *>$null
Write-Progress -Activity "Installing Python Packages" -Completed

Write-Progress -Activity "Upgrading pip" -Status "Running pip install --upgrade pip..." -PercentComplete -1
& "$AppDir\venv\Scripts\python.exe" -m pip install --upgrade pip *>$null
Write-Progress -Activity "Upgrading pip" -Completed

Copy-Item "$AppDir\repo\scripts\launcher.cmd" "$BinDir\InventorySystem.cmd" -Force

Write-Host "Installed InventorySystem $LatestTag"
Write-Host "Start the server by running 'InventorySystem' from the command line."