$ErrorActionPreference = "Stop"

$APP_DIR = "$env:LOCALAPPDATA\InventorySystem"
$REPO = "$APP_DIR\repo"

if ($env:MYAPP_UPDATE_REEXECED -ne "1") {
    git -C "$REPO" fetch --tags --quiet

    $CURRENT_TAG_RAW = git -C "$REPO" describe --tags --exact-match 2>$null
    $CURRENT_TAG = if ($CURRENT_TAG_RAW) { $CURRENT_TAG_RAW.Trim() } else { "unknown" }
    
    $LATEST_TAG_RAW = git -C "$REPO" tag --sort=-v:refname
    $LATEST_TAG = if ($LATEST_TAG_RAW) { ($LATEST_TAG_RAW | Select-Object -First 1).Trim() } else { $null }

    if ($CURRENT_TAG -eq $LATEST_TAG) {
        Write-Host "Already up to date ($CURRENT_TAG)."
        exit 0
    }

    if (-not $LATEST_TAG) {
        Write-Host "No tags found. Falling back to main branch..."
        git -C "$REPO" checkout main
    } else {
        Write-Host "Updating $CURRENT_TAG -> $LATEST_TAG"
        git -C "$REPO" checkout "$LATEST_TAG"
    }

    git -C "$REPO" pull --ff-only

    $env:MYAPP_UPDATE_REEXECED = "1"
    & powershell.exe -ExecutionPolicy Bypass -File "$REPO\scripts\update.ps1" @args
    exit
}

$VENV_PYTHON = "$APP_DIR\venv\Scripts\python.exe"

Write-Host "Updating virtual environment..."
& $VENV_PYTHON -m pip install --upgrade -r "$REPO\requirements.txt"

$BinDir = "$HOME\.local\bin"
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
}

Copy-Item -Path "$REPO\scripts\launcher.ps1" -Destination "$BinDir\InventorySystem.ps1" -Force
Write-Host "Launcher script updated. [$BinDir\InventorySystem.ps1]"

$CommitHash = (git -C "$REPO" rev-parse --short HEAD).Trim()
Write-Host "Updated to $CommitHash"