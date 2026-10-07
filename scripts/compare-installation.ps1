[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TargetRepo
)

$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path -Parent $PSScriptRoot
$targetRoot = [IO.Path]::GetFullPath($TargetRepo)
if (-not (Test-Path -LiteralPath $targetRoot -PathType Container)) {
    throw "Target repository does not exist: $targetRoot"
}

$files = [ordered]@{
    'standard/WORKFLOW_MODES.md' = '.codex/WORKFLOW_MODES.md'
    'standard/ORCHESTRATION.md' = '.codex/ORCHESTRATION.md'
    'standard/PLANNING_HANDOFF.md' = '.codex/PLANNING_HANDOFF.md'
    'skills/complexity-discipline/SKILL.md' = '.agents/skills/complexity-discipline/SKILL.md'
}
foreach ($role in Get-ChildItem -LiteralPath (Join-Path $sourceRoot '.codex/agents') -Filter '*.toml') {
    $relative = '.codex/agents/' + $role.Name
    $files[$relative] = $relative
}

# Adapters and merged AGENTS fragments intentionally have no parity requirement.
# Normalize line endings only: other whitespace can carry Markdown/TOML semantics.
foreach ($entry in $files.GetEnumerator()) {
    $source = Join-Path $sourceRoot $entry.Key
    $target = Join-Path $targetRoot $entry.Value
    $status = 'missing'
    if (Test-Path -LiteralPath $target -PathType Leaf) {
        if ((Get-FileHash -LiteralPath $source).Hash -eq (Get-FileHash -LiteralPath $target).Hash) {
            $status = 'identical'
        } else {
            $sourceText = [IO.File]::ReadAllText($source).Replace("`r`n", "`n")
            $targetText = [IO.File]::ReadAllText($target).Replace("`r`n", "`n")
            $status = if ($sourceText -ceq $targetText) { 'line-endings-only' } else { 'review-required' }
        }
    }
    [pscustomobject]@{ Path = $entry.Value; Status = $status }
}

foreach ($name in @('luna_implementer.toml', 'terra_explorer.toml', 'terra_workhorse.toml', 'terra_reviewer.toml', 'sol_reviewer.toml')) {
    $relative = ".codex/agents/$name"
    if (Test-Path -LiteralPath (Join-Path $targetRoot $relative) -PathType Leaf) {
        [pscustomobject]@{ Path = $relative; Status = 'retired-role-present' }
    }
}
