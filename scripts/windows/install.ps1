$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/Haklyne-dev/InventorySystem.git"
$AppDir  = "$env:LOCALAPPDATA\InventorySystem"
$BinDir  = "$env:LOCALAPPDATA\Microsoft\WindowsApps"  # already on PATH by default on Win10/11

New-Item -ItemType Directory -Force -Path $AppDir | Out-Null

if (Test-Path "$AppDir\repo\.git") {
    git -C "$AppDir\repo" fetch --tags --quiet
} else {
    git clone $RepoUrl "$AppDir\repo"
}

$LatestTag = git -C "$AppDir\repo" tag --sort=-v:refname | Select-Object -First 1
git -C "$AppDir\repo" checkout $LatestTag

python -m venv "$AppDir\venv"
& "$AppDir\venv\Scripts\python.exe" -m pip install -r "$AppDir\repo\requirements.txt"

Copy-Item "$AppDir\repo\scripts\launcher.cmd" "$BinDir\InventorySystem.cmd" -Force

Write-Host "Installed InventorySystem $LatestTag"