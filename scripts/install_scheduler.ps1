# Registers a daily 8:30 AM Task Scheduler job for MemoryFlashcards.
# Same pattern as Connections (DailyConnections) and Sarita Romance Daily.
# Run once from PowerShell: .\scripts\install_scheduler.ps1
#
# If 8:30 is missed (PC asleep or off), StartWhenAvailable runs it at next logon.
# Does not wake the PC from sleep (matches the other daily tasks).

$ErrorActionPreference = "Stop"

$TaskName = "MemoryFlashcards Daily Review"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$RunScript = Join-Path $PSScriptRoot "run_daily.ps1"

if (-not (Test-Path $RunScript)) {
    Write-Error "Missing launcher: $RunScript"
}

$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoExit -ExecutionPolicy Bypass -File `"$RunScript`"" `
    -WorkingDirectory $RepoRoot

$Trigger = New-ScheduledTaskTrigger -Daily -At "8:30AM"

$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 4)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Daily Spanish flashcard review at 8:30 AM; opens terminal, press Enter to close" `
    -Force

Write-Host "Registered scheduled task '$TaskName' - runs daily at 8:30 AM."
Write-Host "  Launcher: $RunScript"
Write-Host "  If missed: runs at next logon (StartWhenAvailable)"
Write-Host ""
Write-Host "To test now: Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "To remove:   Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
