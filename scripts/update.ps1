$ErrorActionPreference = "Stop"

AppDir = "$env:LOCALAPPDATA\InventorySystem"
$Repo   = "$AppDir\repo"
 
git -C $Repo fetch --tags --quiet
 
$CurrentTag = try { git -C $Repo describe --tags --exact-match 2>$null } catch { "unknown" }
if (-not $CurrentTag) { $CurrentTag = "unknown" }
$LatestTag = git -C $Repo tag --sort=-v:refname | Select-Object -First 1
 
if ($CurrentTag -eq $LatestTag) {
    Write-Host "Already up to date ($CurrentTag)."
    exit 0
}

Write-Host "Updating $CurrentTag -> $LatestTag"
git -C $Repo checkout $LatestTag
Set-Content -Path "$Repo\VERSION" -Value $LatestTag