[CmdletBinding()]
param(
    [string]$SessionsRoot = (Join-Path $HOME '.codex\sessions'),
    [int]$Limit = 20,
    [string]$CwdContains
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $SessionsRoot -PathType Container)) {
    throw "Codex sessions directory does not exist: $SessionsRoot"
}

if ($Limit -lt 1) { throw '-Limit must be 1 or greater.' }

function Convert-ToTimestamp {
    param($Value)
    if (-not $Value) { return $null }
    try { return [datetimeoffset]$Value } catch { return $null }
}

$rows = [System.Collections.Generic.List[object]]::new()

foreach ($file in Get-ChildItem $SessionsRoot -Recurse -Filter 'rollout-*.jsonl' -File) {
    $meta = $null
    $active = $null
    $turnNumber = 0
    $lastTimestamp = $null

    foreach ($line in Get-Content -LiteralPath $file.FullName) {
        try {
            $event = $line | ConvertFrom-Json -ErrorAction Stop
        } catch {
            continue
        }

        $timestamp = Convert-ToTimestamp $event.timestamp
        if ($timestamp) { $lastTimestamp = $timestamp }

        if (-not $meta -and $event.type -eq 'session_meta') {
            $meta = if ($event.payload.meta) { $event.payload.meta } else { $event.payload }
            if ($meta.parent_thread_id) { break }
            if ($CwdContains -and ([string]$meta.cwd -notlike "*$CwdContains*")) { break }
            continue
        }

        if (-not $meta -or $event.type -ne 'event_msg') { continue }

        if ($event.payload.type -eq 'task_started') {
            if ($active) {
                $active.CompletedAt = $timestamp
                $active.Status = 'incomplete'
                $rows.Add([PSCustomObject]$active)
            }

            $turnNumber++
            $active = [ordered]@{
                StartedAt = $timestamp
                CompletedAt = $null
                Status = 'running'
                Thread = [string]$meta.id
                Turn = $turnNumber
                TurnId = [string]$event.payload.turn_id
                Cwd = [string]$meta.cwd
                Message = ''
                File = $file.FullName
            }
            continue
        }

        if ($active -and $event.payload.type -eq 'user_message' -and -not $active.Message) {
            $message = ([string]$event.payload.message -replace '\s+', ' ').Trim()
            if ($message.Length -gt 120) { $message = $message.Substring(0, 117) + '...' }
            $active.Message = $message
            continue
        }

        if (
            $active -and
            $event.payload.type -eq 'task_complete' -and
            [string]$event.payload.turn_id -eq [string]$active.TurnId
        ) {
            $active.CompletedAt = $timestamp
            $active.Status = 'complete'
            $rows.Add([PSCustomObject]$active)
            $active = $null
        }
    }

    if ($meta -and -not $meta.parent_thread_id -and $active) {
        $active.CompletedAt = $lastTimestamp
        $active.Status = 'incomplete'
        $rows.Add([PSCustomObject]$active)
    }
}

$rows |
    Sort-Object StartedAt -Descending |
    Select-Object -First $Limit |
    Format-Table StartedAt, Thread, Turn, TurnId, Status, Cwd, Message -AutoSize
