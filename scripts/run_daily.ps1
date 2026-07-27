Set-Location (Split-Path -Parent $PSScriptRoot)
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
chcp 65001 | Out-Null
python main.py
Write-Host ""
Read-Host "Press Enter to close"
