[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$TargetRepo)

$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path -Parent $PSScriptRoot
$targetRoot = [IO.Path]::GetFullPath($TargetRepo)
if (-not (Test-Path -LiteralPath $targetRoot -PathType Container)) { throw "Missing target: $targetRoot" }

# Adapters and merged instructions deliberately have no byte-parity requirement.
foreach ($role in Get-ChildItem -LiteralPath (Join-Path $sourceRoot '.codex/agents') -Filter '*.toml') {
    $relative = ".codex/agents/$($role.Name)"
    $target = Join-Path $targetRoot $relative
    $status = 'not-installed-optional'
    if (Test-Path -LiteralPath $target -PathType Leaf) {
        $sourceText = [IO.File]::ReadAllText($role.FullName).Replace("`r`n", "`n")
        $targetText = [IO.File]::ReadAllText($target).Replace("`r`n", "`n")
        $status = if ($sourceText -ceq $targetText) { 'identical' } else { 'review-local-adaptation' }
    }
    [pscustomobject]@{ Path = $relative; Status = $status }
}
foreach ($relative in @('.codex/WORKFLOW_MODES.md', '.codex/ORCHESTRATION.md', '.codex/PLANNING_HANDOFF.md', '.codex/AGENTS-delegation.md')) {
    if (Test-Path -LiteralPath (Join-Path $targetRoot $relative)) {
        [pscustomobject]@{ Path = $relative; Status = 'legacy-workflow-review-before-retiring' }
    }
}
foreach ($name in @('luna_implementer', 'terra_explorer', 'terra_workhorse', 'terra_reviewer', 'sol_reviewer')) {
    $relative = ".codex/agents/$name.toml"
    if (Test-Path -LiteralPath (Join-Path $targetRoot $relative)) {
        [pscustomobject]@{ Path = $relative; Status = 'retired-role-present' }
    }
}
foreach ($skill in Get-ChildItem -LiteralPath (Join-Path $sourceRoot 'skills') -Directory) {
    $relative = ".agents/skills/$($skill.Name)/SKILL.md"
    if (Test-Path -LiteralPath (Join-Path $targetRoot $relative)) {
        [pscustomobject]@{ Path = $relative; Status = 'local-skill-review-for-duplicate-or-adaptation' }
    }
}
