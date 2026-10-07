[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RootThread,

    [string]$SessionsRoot = (Join-Path $HOME '.codex\sessions'),

    [string]$OutDir = (Join-Path $HOME 'Desktop\codex-trace'),

    [string]$TurnId,

    [int]$TurnNumber = 0,

    [switch]$ListTurns
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $SessionsRoot -PathType Container)) {
    throw "Codex sessions directory does not exist: $SessionsRoot"
}

$hasTurnNumber = $PSBoundParameters.ContainsKey('TurnNumber')
if ($TurnId -and $hasTurnNumber) {
    throw 'Specify either -TurnId or -TurnNumber, not both.'
}

function Convert-ToTimestamp {
    param($Value)

    if (-not $Value) { return $null }
    try { return [datetimeoffset]$Value } catch { return $null }
}

function Get-SessionMeta {
    param([Parameter(Mandatory = $true)][string]$Path)

    foreach ($line in Get-Content -LiteralPath $Path) {
        try {
            $event = $line | ConvertFrom-Json -ErrorAction Stop
        } catch {
            continue
        }

        if ($event.type -eq 'session_meta') {
            if ($event.payload.meta) { return $event.payload.meta }
            return $event.payload
        }
    }

    return $null
}

function Get-RootTurns {
    param([Parameter(Mandatory = $true)][string]$Path)

    $turns = [System.Collections.Generic.List[object]]::new()
    $active = $null
    $number = 0
    $lastTimestamp = $null

    foreach ($line in Get-Content -LiteralPath $Path) {
        try {
            $event = $line | ConvertFrom-Json -ErrorAction Stop
        } catch {
            continue
        }

        $timestamp = Convert-ToTimestamp $event.timestamp
        if ($timestamp) { $lastTimestamp = $timestamp }

        if ($event.type -ne 'event_msg') { continue }

        if ($event.payload.type -eq 'task_started') {
            if ($active) {
                $active.End = $timestamp
                $active.Status = 'incomplete'
                $turns.Add([PSCustomObject]$active)
            }

            $number++
            $active = [ordered]@{
                Number = $number
                TurnId = [string]$event.payload.turn_id
                Start = $timestamp
                End = $null
                Status = 'running'
                Message = ''
            }
            continue
        }

        if ($active -and $event.payload.type -eq 'user_message' -and -not $active.Message) {
            $active.Message = [string]$event.payload.message
            continue
        }

        if (
            $active -and
            $event.payload.type -eq 'task_complete' -and
            [string]$event.payload.turn_id -eq [string]$active.TurnId
        ) {
            $active.End = $timestamp
            $active.Status = 'complete'
            $turns.Add([PSCustomObject]$active)
            $active = $null
        }
    }

    if ($active) {
        $active.End = $lastTimestamp
        $active.Status = 'incomplete'
        $turns.Add([PSCustomObject]$active)
    }

    return $turns
}

function Get-FirstTimestamp {
    param([Parameter(Mandatory = $true)][string]$Path)

    foreach ($line in Get-Content -LiteralPath $Path) {
        try {
            $event = $line | ConvertFrom-Json -ErrorAction Stop
        } catch {
            continue
        }

        $timestamp = Convert-ToTimestamp $event.timestamp
        if ($timestamp) { return $timestamp }
    }

    return $null
}

function Test-InWindow {
    param(
        [datetimeoffset]$Timestamp,
        [datetimeoffset]$Start,
        $End
    )

    if ($Timestamp -lt $Start) { return $false }
    if ($null -ne $End -and $Timestamp -gt [datetimeoffset]$End) { return $false }
    return $true
}

function Get-UsageValue {
    param($Usage, [string]$Property)
    if (-not $Usage) { return [long]0 }
    return [long]$Usage.$Property
}

$allSessions = @{}

foreach ($file in Get-ChildItem $SessionsRoot -Recurse -Filter 'rollout-*.jsonl' -File) {
    $meta = Get-SessionMeta -Path $file.FullName
    if (-not $meta) { continue }

    $id = [string]$meta.id
    if (-not $id) { continue }

    $allSessions[$id] = [PSCustomObject]@{
        File = $file
        Meta = $meta
    }
}

if (-not $allSessions.ContainsKey($RootThread)) {
    throw "Root thread was not found under $SessionsRoot`: $RootThread"
}

$rootSession = $allSessions[$RootThread]
$rootTurns = @(Get-RootTurns -Path $rootSession.File.FullName)

if ($ListTurns) {
    $rootTurns | ForEach-Object {
        $message = ($_.Message -replace '\s+', ' ').Trim()
        if ($message.Length -gt 140) { $message = $message.Substring(0, 137) + '...' }
        $duration = if ($_.Start -and $_.End) {
            [Math]::Round(($_.End - $_.Start).TotalMinutes, 2)
        } else {
            $null
        }

        [PSCustomObject]@{
            Number = $_.Number
            TurnId = $_.TurnId
            StartedAt = $_.Start
            CompletedAt = $_.End
            DurationMinutes = $duration
            Status = $_.Status
            Message = $message
        }
    } | Format-Table -AutoSize
    return
}

$selectedTurn = $null
if ($TurnId) {
    $selectedTurn = $rootTurns | Where-Object { $_.TurnId -eq $TurnId } | Select-Object -First 1
    if (-not $selectedTurn) { throw "Turn ID was not found in root thread $RootThread`: $TurnId" }
} elseif ($hasTurnNumber) {
    if ($TurnNumber -lt 1) { throw '-TurnNumber must be 1 or greater.' }
    $selectedTurn = $rootTurns | Where-Object { $_.Number -eq $TurnNumber } | Select-Object -First 1
    if (-not $selectedTurn) { throw "Turn number was not found in root thread $RootThread`: $TurnNumber" }
}

$selectionStart = if ($selectedTurn) { [datetimeoffset]$selectedTurn.Start } else { $null }
$selectionEnd = if ($selectedTurn -and $selectedTurn.End) { [datetimeoffset]$selectedTurn.End } else { $null }
$scope = if ($selectedTurn) { 'turn' } else { 'thread' }

$descendantCache = @{}

function Test-IsInRun {
    param([Parameter(Mandatory = $true)][string]$ThreadId)

    if ($descendantCache.ContainsKey($ThreadId)) {
        return [bool]$descendantCache[$ThreadId]
    }

    $seen = [System.Collections.Generic.HashSet[string]]::new()
    $current = $ThreadId

    while ($current) {
        if ($current -eq $RootThread) {
            $descendantCache[$ThreadId] = $true
            return $true
        }

        if (-not $seen.Add($current)) { break }
        if (-not $allSessions.ContainsKey($current)) { break }
        $current = [string]$allSessions[$current].Meta.parent_thread_id
    }

    $descendantCache[$ThreadId] = $false
    return $false
}

$runSessions = $allSessions.Keys |
    Where-Object { Test-IsInRun -ThreadId $_ } |
    ForEach-Object { $allSessions[$_] }

if ($selectedTurn) {
    $runSessions = $runSessions | Where-Object {
        $id = [string]$_.Meta.id
        if ($id -eq $RootThread) { return $true }
        $startedAt = Get-FirstTimestamp -Path $_.File.FullName
        if (-not $startedAt) { return $false }
        return Test-InWindow -Timestamp $startedAt -Start $selectionStart -End $selectionEnd
    }
}

$summaryRows = [System.Collections.Generic.List[object]]::new()
$eventRows = [System.Collections.Generic.List[object]]::new()

foreach ($session in $runSessions) {
    $file = $session.File
    $meta = $session.Meta
    $isSelectedRoot = $selectedTurn -and ([string]$meta.id -eq $RootThread)
    $firstTurn = $null
    $baselineUsage = $null
    $previousUsage = $null
    $lastUsage = $null
    $usageIndex = 0
    $firstTimestamp = $null
    $lastTimestamp = $null

    foreach ($line in Get-Content -LiteralPath $file.FullName) {
        try {
            $event = $line | ConvertFrom-Json -ErrorAction Stop
        } catch {
            continue
        }

        $timestamp = Convert-ToTimestamp $event.timestamp
        $inWindow = $true
        if ($isSelectedRoot -and $timestamp) {
            $inWindow = Test-InWindow -Timestamp $timestamp -Start $selectionStart -End $selectionEnd
        }

        if ($timestamp -and $inWindow) {
            if (-not $firstTimestamp) { $firstTimestamp = $timestamp }
            $lastTimestamp = $timestamp
        }

        if ($event.type -eq 'turn_context' -and -not $firstTurn -and $inWindow) {
            $firstTurn = $event.payload
        }

        if (
            $event.type -eq 'event_msg' -and
            $event.payload.type -eq 'token_count' -and
            $event.payload.info.total_token_usage
        ) {
            $u = $event.payload.info.total_token_usage

            if ($isSelectedRoot -and $timestamp -and $timestamp -lt $selectionStart) {
                $baselineUsage = $u
                $previousUsage = $u
                continue
            }

            if (-not $inWindow) { continue }

            $usageIndex++
            $baseInput = Get-UsageValue $baselineUsage 'input_tokens'
            $baseCached = Get-UsageValue $baselineUsage 'cached_input_tokens'
            $baseOutput = Get-UsageValue $baselineUsage 'output_tokens'
            $baseReasoning = Get-UsageValue $baselineUsage 'reasoning_output_tokens'

            $input = [Math]::Max(0, [long]$u.input_tokens - $baseInput)
            $cached = [Math]::Max(0, [long]$u.cached_input_tokens - $baseCached)
            $output = [Math]::Max(0, [long]$u.output_tokens - $baseOutput)
            $reasoning = [Math]::Max(0, [long]$u.reasoning_output_tokens - $baseReasoning)
            $uncached = [Math]::Max(0, $input - $cached)

            if ($previousUsage) {
                $deltaInput = [Math]::Max(0, [long]$u.input_tokens - [long]$previousUsage.input_tokens)
                $deltaCached = [Math]::Max(0, [long]$u.cached_input_tokens - [long]$previousUsage.cached_input_tokens)
                $deltaOutput = [Math]::Max(0, [long]$u.output_tokens - [long]$previousUsage.output_tokens)
                $deltaReasoning = [Math]::Max(0, [long]$u.reasoning_output_tokens - [long]$previousUsage.reasoning_output_tokens)
            } else {
                $deltaInput = $input
                $deltaCached = $cached
                $deltaOutput = $output
                $deltaReasoning = $reasoning
            }

            $eventRows.Add([PSCustomObject]@{
                Scope = $scope
                TurnNumber = if ($selectedTurn) { $selectedTurn.Number } else { $null }
                TurnId = if ($selectedTurn) { $selectedTurn.TurnId } else { '' }
                Timestamp = [string]$event.timestamp
                Thread = [string]$meta.id
                Parent = [string]$meta.parent_thread_id
                AgentRole = [string]$meta.agent_role
                AgentPath = [string]$meta.agent_path
                Model = [string]$firstTurn.model
                Effort = [string]$firstTurn.effort
                Sandbox = [string]$firstTurn.sandbox_policy.type
                EventNumber = $usageIndex
                InputTokens = $input
                CachedInputTokens = $cached
                UncachedInputTokens = $uncached
                OutputTokens = $output
                ReasoningTokens = $reasoning
                TotalTokens = $input + $output
                CachePercent = if ($input -gt 0) { [Math]::Round(($cached / $input) * 100, 1) } else { 0 }
                DeltaInputTokens = $deltaInput
                DeltaCachedInputTokens = $deltaCached
                DeltaUncachedInputTokens = [Math]::Max(0, $deltaInput - $deltaCached)
                DeltaOutputTokens = $deltaOutput
                DeltaReasoningTokens = $deltaReasoning
            })

            $previousUsage = $u
            $lastUsage = $u
        }
    }

    if (-not $lastUsage) { continue }

    $baseInput = Get-UsageValue $baselineUsage 'input_tokens'
    $baseCached = Get-UsageValue $baselineUsage 'cached_input_tokens'
    $baseOutput = Get-UsageValue $baselineUsage 'output_tokens'
    $baseReasoning = Get-UsageValue $baselineUsage 'reasoning_output_tokens'

    $input = [Math]::Max(0, [long]$lastUsage.input_tokens - $baseInput)
    $cached = [Math]::Max(0, [long]$lastUsage.cached_input_tokens - $baseCached)
    $output = [Math]::Max(0, [long]$lastUsage.output_tokens - $baseOutput)
    $reasoning = [Math]::Max(0, [long]$lastUsage.reasoning_output_tokens - $baseReasoning)

    $threadSource = if ($meta.thread_source -is [string]) {
        [string]$meta.thread_source
    } elseif ($meta.thread_source) {
        $meta.thread_source | ConvertTo-Json -Compress
    } else {
        ''
    }

    $durationMinutes = if ($isSelectedRoot -and $selectedTurn.Start -and $selectedTurn.End) {
        [Math]::Round((([datetimeoffset]$selectedTurn.End) - ([datetimeoffset]$selectedTurn.Start)).TotalMinutes, 2)
    } elseif ($firstTimestamp -and $lastTimestamp) {
        [Math]::Round(($lastTimestamp - $firstTimestamp).TotalMinutes, 2)
    } else {
        $null
    }

    $summaryRows.Add([PSCustomObject]@{
        Scope = $scope
        TurnNumber = if ($selectedTurn) { $selectedTurn.Number } else { $null }
        TurnId = if ($selectedTurn) { $selectedTurn.TurnId } else { '' }
        Thread = [string]$meta.id
        Parent = [string]$meta.parent_thread_id
        Source = $threadSource
        AgentRole = [string]$meta.agent_role
        AgentPath = [string]$meta.agent_path
        Model = [string]$firstTurn.model
        Effort = [string]$firstTurn.effort
        Sandbox = [string]$firstTurn.sandbox_policy.type
        CliVersion = [string]$meta.cli_version
        TokenEvents = $usageIndex
        DurationMinutes = $durationMinutes
        InputTokens = $input
        CachedInputTokens = $cached
        UncachedInputTokens = [Math]::Max(0, $input - $cached)
        OutputTokens = $output
        ReasoningTokens = $reasoning
        NonReasoningOutput = [Math]::Max(0, $output - $reasoning)
        TotalTokens = $input + $output
        CachePercent = if ($input -gt 0) { [Math]::Round(($cached / $input) * 100, 1) } else { 0 }
        RolloutFile = $file.FullName
    })
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$suffix = if ($selectedTurn) { "-turn-$($selectedTurn.Number)" } else { '' }
$summaryPath = Join-Path $OutDir ("$RootThread$suffix-token-summary.csv")
$eventsPath = Join-Path $OutDir ("$RootThread$suffix-token-events.csv")

$summaryRows |
    Sort-Object AgentRole, AgentPath, Thread |
    Export-Csv -LiteralPath $summaryPath -NoTypeInformation -Encoding UTF8

$eventRows |
    Sort-Object Thread, EventNumber |
    Export-Csv -LiteralPath $eventsPath -NoTypeInformation -Encoding UTF8

Write-Host 'Saved rollout metrics:' -ForegroundColor Green
Write-Host "  scope: $scope"
if ($selectedTurn) {
    Write-Host "  turn:  $($selectedTurn.Number) ($($selectedTurn.TurnId))"
}
Write-Host "  $summaryPath"
Write-Host "  $eventsPath"
Write-Host "Sessions in run: $($summaryRows.Count)"
