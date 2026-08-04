# register_apex_task.ps1
# PowerShell script to register or unregister the Apex Ghost Daily Protocol in Windows Task Scheduler.

param (
    [switch]$Unregister
)

$TaskName = "ApexGhostDailyProtocol"

if ($Unregister) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Apex Ghost Daily Protocol task successfully removed from Task Scheduler." -ForegroundColor Green
    } else {
        Write-Host "Task '$TaskName' not found." -ForegroundColor Yellow
    }
    exit 0
}

# Resolve target directory and configuration paths
$ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$ConfigPath = Join-Path $ScriptDir "core\apex_ghost_config.json"
$LauncherPath = Join-Path $ScriptDir "apex.bat"

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Configuration file not found: $ConfigPath"
    exit 1
}

if (-not (Test-Path $LauncherPath)) {
    Write-Error "Launcher bat script not found: $LauncherPath"
    exit 1
}

# Parse wake-up time from config
$Config = Get-Content $ConfigPath | ConvertFrom-Json
$TargetHour = $Config.awakening.target_hour
$TargetMinute = $Config.awakening.target_minute

# Format target time (HH:mm)
$TriggerTime = "{0:D2}:{1:D2}" -f $TargetHour, $TargetMinute

Write-Host "Configured Morning Wake-up Time detected: $TriggerTime" -ForegroundColor Cyan
Write-Host "Launcher path: $LauncherPath" -ForegroundColor Cyan

# Create Scheduled Task Action
$Action = New-ScheduledTaskAction -Execute $LauncherPath -Argument "daily" -WorkingDirectory $ScriptDir

# Create Trigger (Daily at target time)
$Trigger = New-ScheduledTaskTrigger -Daily -At $TriggerTime

# Create Settings (Allow start on demand, wake the computer if supported)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun

# Register the Scheduled Task
$Task = Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Immersive Morning Awakening and Daily Quest System for Apex Ghost" -Force

Write-Host "Apex Ghost Daily Protocol successfully scheduled daily at $TriggerTime!" -ForegroundColor Green
Write-Host "Task settings configured to allow running on battery and wake computer from sleep." -ForegroundColor Green
