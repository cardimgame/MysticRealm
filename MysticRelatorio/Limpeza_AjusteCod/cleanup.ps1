# tools/cleanup.ps1
# Remove empty directories (recursively)
Get-ChildItem -Recurse -Directory | Where-Object {($_.GetFileSystemInfos().Count -eq 0)} | Remove-Item -Force -Recurse

# Prefer systems/inventory.py and delete gameplay/inventory.py if both exist
$keep = Join-Path $PSScriptRoot '..\systems\inventory.py' | Resolve-Path
$dupe = Join-Path $PSScriptRoot '..\gameplay\inventory.py'
if (Test-Path $keep) { if (Test-Path $dupe) { Remove-Item $dupe -Force } }
