[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

function Assert-Equal {
    param($Actual, $Expected, [string]$Message)
    if ([string]$Actual -ne [string]$Expected) {
        throw "$Message. Expected '$Expected', got '$Actual'."
    }
}

$root = Join-Path ([System.IO.Path]::GetTempPath()) ("codex-rollout-test-" + [guid]::NewGuid().ToString('N'))
$sessions = Join-Path $root 'sessions'
$out = Join-Path $root 'out'
New-Item -ItemType Directory -Force -Path $sessions, $out | Out-Null

try {
    # Dated role labels below represent archived rollout metadata; the exporter must read them without requiring current registrations.
    @'
{"timestamp":"2026-08-09T00:00:00Z","type":"session_meta","payload":{"id":"root-thread","parent_thread_id":null,"thread_source":"user","cwd":"C:\\repo","cli_version":"test"}}
{"timestamp":"2026-08-09T00:00:01Z","type":"event_msg","payload":{"type":"task_started","turn_id":"turn-one"}}
{"timestamp":"2026-08-09T00:00:02Z","type":"event_msg","payload":{"type":"user_message","message":"first task"}}
{"timestamp":"2026-08-09T00:00:03Z","type":"turn_context","payload":{"model":"gpt-test","effort":"medium","sandbox_policy":{"type":"test"}}}
{"timestamp":"2026-08-09T00:01:00Z","type":"event_msg","payload":{"type":"token_count","info":{"total_token_usage":{"input_tokens":100,"cached_input_tokens":60,"output_tokens":10,"reasoning_output_tokens":4}}}}
{"timestamp":"2026-08-09T00:02:00Z","type":"event_msg","payload":{"type":"task_complete","turn_id":"turn-one"}}
{"timestamp":"2026-08-09T00:10:00Z","type":"event_msg","payload":{"type":"task_started","turn_id":"turn-two"}}
{"timestamp":"2026-08-09T00:10:01Z","type":"event_msg","payload":{"type":"user_message","message":"second task"}}
{"timestamp":"2026-08-09T00:10:02Z","type":"turn_context","payload":{"model":"gpt-test","effort":"medium","sandbox_policy":{"type":"test"}}}
{"timestamp":"2026-08-09T00:10:30Z","type":"event_msg","payload":{"type":"token_count","info":{"total_token_usage":{"input_tokens":160,"cached_input_tokens":100,"output_tokens":15,"reasoning_output_tokens":6}}}}
{"timestamp":"2026-08-09T00:11:00Z","type":"event_msg","payload":{"type":"task_complete","turn_id":"turn-two"}}
'@ | Set-Content -LiteralPath (Join-Path $sessions 'rollout-root.jsonl') -Encoding UTF8

    @'
{"timestamp":"2026-08-09T00:00:30Z","type":"session_meta","payload":{"id":"child-one","parent_thread_id":"root-thread","thread_source":"subagent","agent_role":"luna_implementer","agent_path":"/root/task-one","cli_version":"test"}}
{"timestamp":"2026-08-09T00:00:31Z","type":"turn_context","payload":{"model":"gpt-child","effort":"high","sandbox_policy":{"type":"test"}}}
{"timestamp":"2026-08-09T00:01:30Z","type":"event_msg","payload":{"type":"token_count","info":{"total_token_usage":{"input_tokens":50,"cached_input_tokens":20,"output_tokens":5,"reasoning_output_tokens":2}}}}
'@ | Set-Content -LiteralPath (Join-Path $sessions 'rollout-child-one.jsonl') -Encoding UTF8

    @'
{"timestamp":"2026-08-09T00:10:15Z","type":"session_meta","payload":{"id":"child-two","parent_thread_id":"root-thread","thread_source":"subagent","agent_role":"terra_reviewer","agent_path":"/root/task-two-review","cli_version":"test"}}
{"timestamp":"2026-08-09T00:10:16Z","type":"turn_context","payload":{"model":"gpt-child","effort":"high","sandbox_policy":{"type":"test"}}}
{"timestamp":"2026-08-09T00:10:40Z","type":"event_msg","payload":{"type":"token_count","info":{"total_token_usage":{"input_tokens":70,"cached_input_tokens":30,"output_tokens":7,"reasoning_output_tokens":3}}}}
'@ | Set-Content -LiteralPath (Join-Path $sessions 'rollout-child-two.jsonl') -Encoding UTF8

    $exporter = Join-Path $PSScriptRoot 'export-rollout-metrics.ps1'
    $finder = Join-Path $PSScriptRoot 'list-codex-root-tasks.ps1'

    & $exporter -RootThread 'root-thread' -SessionsRoot $sessions -OutDir $out -TurnNumber 1 | Out-Null
    $turn1 = Import-Csv -LiteralPath (Join-Path $out 'root-thread-turn-1-token-summary.csv')
    Assert-Equal $turn1.Count 2 'Turn 1 should include the root and only its child'
    $turn1Root = $turn1 | Where-Object Thread -eq 'root-thread'
    Assert-Equal $turn1Root.InputTokens 100 'Turn 1 root input should be relative to zero'
    Assert-Equal $turn1Root.UncachedInputTokens 40 'Turn 1 root uncached input should be relative to zero'
    Assert-Equal $turn1Root.OutputTokens 10 'Turn 1 root output should be relative to zero'
    Assert-Equal (($turn1 | Where-Object Thread -eq 'child-one').Count) 1 'Turn 1 should include child one'
    Assert-Equal (($turn1 | Where-Object Thread -eq 'child-two').Count) 0 'Turn 1 should exclude child two'

    & $exporter -RootThread 'root-thread' -SessionsRoot $sessions -OutDir $out -TurnId 'turn-two' | Out-Null
    $turn2 = Import-Csv -LiteralPath (Join-Path $out 'root-thread-turn-2-token-summary.csv')
    Assert-Equal $turn2.Count 2 'Turn 2 should include the root and only its child'
    $turn2Root = $turn2 | Where-Object Thread -eq 'root-thread'
    Assert-Equal $turn2Root.InputTokens 60 'Turn 2 root input should subtract the prior-turn baseline'
    Assert-Equal $turn2Root.CachedInputTokens 40 'Turn 2 root cached input should subtract the prior-turn baseline'
    Assert-Equal $turn2Root.OutputTokens 5 'Turn 2 root output should subtract the prior-turn baseline'
    Assert-Equal $turn2Root.ReasoningTokens 2 'Turn 2 root reasoning should subtract the prior-turn baseline'
    Assert-Equal (($turn2 | Where-Object Thread -eq 'child-one').Count) 0 'Turn 2 should exclude child one'
    Assert-Equal (($turn2 | Where-Object Thread -eq 'child-two').Count) 1 'Turn 2 should include child two'

    & $exporter -RootThread 'root-thread' -SessionsRoot $sessions -OutDir $out | Out-Null
    $whole = Import-Csv -LiteralPath (Join-Path $out 'root-thread-token-summary.csv')
    Assert-Equal $whole.Count 3 'Whole-thread export should remain backward compatible'
    Assert-Equal (($whole | Where-Object Thread -eq 'root-thread').InputTokens) 160 'Whole-thread root totals should remain cumulative'

    $turnListing = (& $exporter -RootThread 'root-thread' -SessionsRoot $sessions -ListTurns | Out-String)
    if ($turnListing -notmatch 'turn-one' -or $turnListing -notmatch 'turn-two') {
        throw 'Exporter turn discovery should show both root turns.'
    }

    $rootListing = (& $finder -SessionsRoot $sessions -Limit 5 | Out-String)
    if ($rootListing -notmatch 'root-thread' -or $rootListing -notmatch 'turn-two') {
        throw 'Root task discovery should include the root thread and its turns.'
    }

    Write-Host 'Rollout metrics smoke tests passed.' -ForegroundColor Green
} finally {
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
