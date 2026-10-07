[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TargetRepo,

    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$sourceRoot = Split-Path -Parent $PSScriptRoot
$targetRoot = [IO.Path]::GetFullPath($TargetRepo)

if (-not (Test-Path -LiteralPath $targetRoot -PathType Container)) {
    throw "Target repository does not exist: $targetRoot"
}

$retiredAgentNames = @(
    'luna_implementer.toml',
    'terra_explorer.toml',
    'terra_workhorse.toml',
    'terra_reviewer.toml',
    'sol_reviewer.toml'
)
$retiredAgentsPresent = @($retiredAgentNames | Where-Object {
    Test-Path -LiteralPath (Join-Path $targetRoot ".codex\agents\$_") -PathType Leaf
})
if ($retiredAgentsPresent.Count -gt 0) {
    throw "Retired role files exist in the target: $($retiredAgentsPresent -join ', '). Reconcile and remove them in the target repository before installing the semantic roles; -Force does not migrate role names."
}

$copied = [System.Collections.Generic.List[string]]::new()
$skipped = [System.Collections.Generic.List[string]]::new()

function Copy-WorkflowFile {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        throw "Workflow source file is missing: $Source"
    }

    if ((Test-Path -LiteralPath $Destination) -and -not $Force) {
        $skipped.Add($Destination)
        return
    }

    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    Copy-Item -LiteralPath $Source -Destination $Destination -Force:$Force
    $copied.Add($Destination)
}

$agentNames = @(
    'bounded_implementer.toml',
    'explorer.toml',
    'integration_workhorse.toml',
    'ordinary_reviewer.toml',
    'exceptional_risk_reviewer.toml'
)

foreach ($name in $agentNames) {
    Copy-WorkflowFile `
        -Source (Join-Path $sourceRoot ".codex\agents\$name") `
        -Destination (Join-Path $targetRoot ".codex\agents\$name")
}

Copy-WorkflowFile `
    -Source (Join-Path $sourceRoot 'standard\WORKFLOW_MODES.md') `
    -Destination (Join-Path $targetRoot '.codex\WORKFLOW_MODES.md')

Copy-WorkflowFile `
    -Source (Join-Path $sourceRoot 'standard\ORCHESTRATION.md') `
    -Destination (Join-Path $targetRoot '.codex\ORCHESTRATION.md')

Copy-WorkflowFile `
    -Source (Join-Path $sourceRoot 'standard\PLANNING_HANDOFF.md') `
    -Destination (Join-Path $targetRoot '.codex\PLANNING_HANDOFF.md')

Copy-WorkflowFile `
    -Source (Join-Path $sourceRoot 'templates\PROJECT.md') `
    -Destination (Join-Path $targetRoot '.codex\PROJECT.md')

$delegationDestination = Join-Path $targetRoot '.codex\AGENTS-delegation.md'
$complexitySkillDestination = Join-Path $targetRoot '.agents\skills\complexity-discipline\SKILL.md'

Copy-WorkflowFile `
    -Source (Join-Path $sourceRoot 'templates\AGENTS-delegation.md') `
    -Destination $delegationDestination

Copy-WorkflowFile `
    -Source (Join-Path $sourceRoot 'skills\complexity-discipline\SKILL.md') `
    -Destination $complexitySkillDestination

Write-Host ''
Write-Host 'Portable Codex workflow installation complete.' -ForegroundColor Green
Write-Host "Target: $targetRoot"
Write-Host "Copied: $($copied.Count)"
Write-Host "Skipped existing files: $($skipped.Count)"

if ($copied.Count -gt 0) {
    Write-Host ''
    Write-Host 'Copied files:'
    foreach ($path in $copied) {
        Write-Host "  + $path"
    }
}

if ($skipped.Count -gt 0) {
    Write-Host ''
    Write-Host 'Existing files left untouched:' -ForegroundColor Yellow
    foreach ($path in $skipped) {
        Write-Host "  = $path"
    }
    Write-Host 'Re-run with -Force only after reviewing local customizations.' -ForegroundColor Yellow
}

if ($copied.Contains($complexitySkillDestination) -and $skipped.Contains($delegationDestination)) {
    Write-Host ''
    Write-Host 'Existing-installation upgrade note:' -ForegroundColor Yellow
    Write-Host '  The complexity-discipline skill was newly installed, but the existing AGENTS delegation fragment was left untouched.' -ForegroundColor Yellow
    Write-Host '  Reconcile the current portable workflow fragment from templates\AGENTS-delegation.md into the repository''s real AGENTS.md before relying on the newly installed workflow skill.' -ForegroundColor Yellow
    Write-Host '  Pay particular attention to Complexity Discipline routing when the skill is newly installed.' -ForegroundColor Yellow
    Write-Host '  Do not use -Force as a blanket upgrade mechanism unless all local workflow customizations have been reviewed.' -ForegroundColor Yellow
}

Write-Host ''
Write-Host 'Next steps:' -ForegroundColor Cyan
Write-Host '  1. Merge .codex\AGENTS-delegation.md into the repository AGENTS.md where appropriate.'
Write-Host '  2. Fill in .codex\PROJECT.md with real docs, commands, ownership boundaries, and risk surfaces.'
Write-Host '  3. Read .codex\WORKFLOW_MODES.md and choose the lightest safe control loop before starting work.'
Write-Host '  4. Restart Codex if needed so the project-local .agents\skills\complexity-discipline skill is discovered.'
Write-Host '  5. Review git diff before committing the imported workflow files.'
Write-Host '  6. Run a harmless fresh-session custom-role smoke test before trusting delegation on important Goal execution work.'
