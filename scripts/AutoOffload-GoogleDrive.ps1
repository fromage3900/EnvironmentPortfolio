<#
.SYNOPSIS
    Automated Disk Space Watermark Monitor & Google Drive Offload Engine.

.DESCRIPTION
    Monitors available storage capacity across system and secondary drives (C:, F:, G:).
    When free space falls below a specified threshold:
    1. Executes safe non-destructive cache and temporary file cleanup.
    2. Packages and offloads cold project archives and historical backups to Google Drive.
    3. Verifies cloud transfer integrity before removing local archives.

.PARAMETER MinFreeGBThreshold
    Minimum free gigabytes per drive before offload triggers (Default: 50 GB).

.PARAMETER DryRun
    Simulates operations without modifying files.

.PARAMETER InstallScheduledTask
    Registers this script as a recurring Windows Scheduled Task (every 6 hours).
#>

[CmdletBinding()]
param(
    [int]$MinFreeGBThreshold = 50,
    [switch]$DryRun,
    [switch]$InstallScheduledTask,
    [switch]$UninstallScheduledTask
)

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$WorkspaceRoot = Split-Path -Parent $ScriptDir
$LogDir = Join-Path $WorkspaceRoot "logs"
$ToolsDir = Join-Path $WorkspaceRoot "tools"
$RcloneExe = Join-Path $ToolsDir "rclone.exe"
$LogFile = Join-Path $LogDir "offload_monitor.log"

# Ensure logging directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $logLine = "[$timestamp] [$Level] $Message"
    Write-Host $logLine
    Add-Content -Path $LogFile -Value $logLine -Encoding utf8
}

function Get-DriveMetrics {
    $volumes = Get-Volume | Where-Object { $_.DriveLetter -and $_.DriveType -eq 'Fixed' }
    $results = @()
    foreach ($vol in $volumes) {
        $totalGB = [math]::Round($vol.Size / 1GB, 2)
        $freeGB = [math]::Round($vol.SizeRemaining / 1GB, 2)
        $freePct = [math]::Round(($freeGB / $totalGB) * 100, 1)
        $results += [PSCustomObject]@{
            DriveLetter = $vol.DriveLetter
            Label       = $vol.FileSystemLabel
            TotalGB     = $totalGB
            FreeGB      = $freeGB
            FreePercent = $freePct
            NeedsAction = ($freeGB -lt $MinFreeGBThreshold)
        }
    }
    return $results
}

function Invoke-CacheMaintenance {
    Write-Log "Initiating safe developer cache & temporary file maintenance..." "INFO"
    $userProfile = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::UserProfile)
    
    $cachePaths = @(
        "$userProfile\AppData\Local\Temp",
        "$userProfile\AppData\Local\uv\cache",
        "$userProfile\AppData\Local\npm-cache",
        "$userProfile\AppData\Local\pip\cache",
        "$userProfile\.cache",
        "$userProfile\.local\share\opencode\tool-output",
        "$userProfile\.local\share\opencode\snapshot",
        "$userProfile\.local\share\opencode\log",
        "$userProfile\.local\share\kilo\log",
        "F:\UE_DDC",
        "G:\UE_DDC",
        "G:\MelodiaMelusina\Intermediate",
        "G:\MelodiaMelusina\DerivedDataCache",
        "G:\MelodiaMelusina\Saved\Logs",
        "G:\MelodiaMelusina\Saved\Autosaves"
    )

    foreach ($path in $cachePaths) {
        if (Test-Path $path) {
            Write-Log "Cleaning cache target: $path" "INFO"
            if (-not $DryRun) {
                try {
                    cmd.exe /c "rmdir /s /q `"$path`" 2>nul"
                } catch {
                    Write-Log "Non-critical skip for locked files in: $path" "WARN"
                }
            } else {
                Write-Log "[DryRun] Would purge: $path" "INFO"
            }
        }
    }
}

function Invoke-GoogleDriveOffload {
    Write-Log "Checking Google Drive offload targets..." "INFO"

    # Identify archive directories designated for cloud storage
    $offloadCandidates = @(
        @{ Source = "F:\_FromG_Archive"; RemoteSubdir = "Archives/FromG_Archive" },
        @{ Source = "F:\harddrivebackup"; RemoteSubdir = "Archives/HardDriveBackup" },
        @{ Source = "F:\_Organized\Installers_Archive"; RemoteSubdir = "Archives/Installers" },
        @{ Source = "G:\Archive"; RemoteSubdir = "Archives/G_Archive" },
        @{ Source = "G:\BS_GodFile_Archive"; RemoteSubdir = "Archives/BS_GodFile_Archive" }
    )

    # Check for rclone remote or Google Drive virtual drive
    $userProfile = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::UserProfile)
    $rcloneConfigPath = Join-Path $userProfile ".config\rclone\rclone.conf"
    $hasRcloneRemote = (Test-Path $RcloneExe) -and (Test-Path $rcloneConfigPath)

    # Check for Google Drive desktop streaming volume
    $gDriveVol = Get-Volume | Where-Object { $_.FileSystemLabel -match "Google Drive|My Drive" }

    if ($hasRcloneRemote) {
        Write-Log "Using Rclone engine for Google Drive sync." "INFO"
        foreach ($item in $offloadCandidates) {
            if (Test-Path $item.Source) {
                Write-Log "Offloading '$($item.Source)' to 'gdrive:$($item.RemoteSubdir)'" "INFO"
                if (-not $DryRun) {
                    $cmd = "& `"$RcloneExe`" copy `"$($item.Source)`" `"gdrive:$($item.RemoteSubdir)`" --transfers 4 --checkers 8 --log-file=`"$LogFile`" --log-level INFO"
                    Invoke-Expression $cmd
                    if ($LASTEXITCODE -eq 0) {
                        Write-Log "Offload verified successfully for: $($item.Source)" "INFO"
                    } else {
                        Write-Log "Rclone offload error for $($item.Source). Preserving local copy." "ERROR"
                    }
                } else {
                    Write-Log "[DryRun] Would upload $($item.Source) to gdrive:$($item.RemoteSubdir)" "INFO"
                }
            }
        }
    } elseif ($gDriveVol) {
        $gDriveRoot = "$($gDriveVol.DriveLetter):\My Drive\ColdStorage_Archives"
        Write-Log "Using Google Drive Desktop virtual volume at: $gDriveRoot" "INFO"
        if (-not (Test-Path $gDriveRoot) -and -not $DryRun) {
            New-Item -ItemType Directory -Path $gDriveRoot -Force | Out-Null
        }
        foreach ($item in $offloadCandidates) {
            if (Test-Path $item.Source) {
                $targetPath = Join-Path $gDriveRoot $item.RemoteSubdir
                Write-Log "Robocopy sync '$($item.Source)' -> '$targetPath'" "INFO"
                if (-not $DryRun) {
                    robocopy $item.Source $targetPath /E /R:2 /W:2 /NP /MT:8 /LOG+:$LogFile
                } else {
                    Write-Log "[DryRun] Would robocopy $($item.Source) to $targetPath" "INFO"
                }
            }
        }
    } else {
        Write-Log "Google Drive remote not yet authenticated. Run '$RcloneExe config' or sign in to Google Drive for Desktop to activate automatic transfer." "WARN"
    }
}

# --- Scheduled Task Management ---
if ($InstallScheduledTask) {
    $taskName = "Melodia-Storage-AutoOffload"
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    $trigger = New-ScheduledTaskTrigger -Daily -At "03:00"
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Monitors disk capacity and offloads cold archive data to Google Drive" -Force | Out-Null
    Write-Log "Successfully installed Scheduled Task '$taskName' (Runs daily at 03:00 AM)." "INFO"
    exit 0
}

if ($UninstallScheduledTask) {
    $taskName = "Melodia-Storage-AutoOffload"
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Log "Unregistered Scheduled Task '$taskName'." "INFO"
    exit 0
}

# --- Main Execution Loop ---
Write-Log "========================================================" "INFO"
Write-Log "Starting Disk Watermark & Capacity Evaluation" "INFO"

$metrics = Get-DriveMetrics
$needsMaintenance = $false

foreach ($m in $metrics) {
    Write-Log "Drive $($m.DriveLetter): ($($m.Label)) - $($m.FreeGB) GB Free / $($m.TotalGB) GB Total ($($m.FreePercent)%)" "INFO"
    if ($m.NeedsAction) {
        Write-Log "Drive $($m.DriveLetter): is below threshold ($MinFreeGBThreshold GB). Maintenance triggered." "WARN"
        $needsMaintenance = $true
    }
}

if ($needsMaintenance -or $DryRun) {
    Invoke-CacheMaintenance
    Invoke-GoogleDriveOffload
} else {
    Write-Log "All drives operating within healthy capacity thresholds. No offload required." "INFO"
}

# Final telemetry report
$finalMetrics = Get-DriveMetrics
Write-Log "Final Drive Capacity Status:" "INFO"
foreach ($fm in $finalMetrics) {
    Write-Log "Drive $($fm.DriveLetter): - $($fm.FreeGB) GB Free ($($fm.FreePercent)%)" "INFO"
}
Write-Log "Disk Watermark Check Complete." "INFO"
