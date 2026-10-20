$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path -Parent $PSScriptRoot
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ("codex-workflow-integration-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testRoot | Out-Null
try {
    $agents = Join-Path $testRoot 'AGENTS.md'
    [IO.File]::WriteAllText($agents, 'Existing project policy must survive.')
    $before = (Get-FileHash -LiteralPath $agents).Hash
    & (Join-Path $PSScriptRoot 'install-into-repo.ps1') -TargetRepo $testRoot -IncludeRoles
    if ((Get-FileHash -LiteralPath $agents).Hash -ne $before) { throw 'Installer changed project policy' }
    if (Test-Path -LiteralPath (Join-Path $testRoot '.agents')) { throw 'Installer copied shared skills' }
    if (Test-Path -LiteralPath (Join-Path $testRoot '.codex/ORCHESTRATION.md')) { throw 'Installer copied old workflow' }
    $role = Join-Path $testRoot '.codex/agents/bounded_implementer.toml'
    [IO.File]::AppendAllText($role, "`n# Local adaptation`n")
    $adapted = (Get-FileHash -LiteralPath $role).Hash
    $fragment = Join-Path $testRoot '.codex/AGENTS-workflow.md'
    [IO.File]::AppendAllText($fragment, "`nLocal integration note.`n")
    $fragmentBefore = (Get-FileHash -LiteralPath $fragment).Hash
    & (Join-Path $PSScriptRoot 'install-into-repo.ps1') -TargetRepo $testRoot -IncludeRoles
    if ((Get-FileHash -LiteralPath $role).Hash -ne $adapted) { throw 'Installer overwrote an adapted role' }
    if ((Get-FileHash -LiteralPath $fragment).Hash -ne $fragmentBefore) { throw 'Installer overwrote integration' }
    $results = @(& (Join-Path $PSScriptRoot 'compare-installation.ps1') -TargetRepo $testRoot)
    if (-not ($results | Where-Object { $_.Path -eq '.codex/agents/bounded_implementer.toml' -and $_.Status -eq 'review-local-adaptation' })) {
        throw 'Comparison missed adapted role'
    }
    [IO.File]::WriteAllText((Join-Path $testRoot '.codex/agents/terra_workhorse.toml'), '# retired role')
    $blocked = $false
    try { & (Join-Path $PSScriptRoot 'install-into-repo.ps1') -TargetRepo $testRoot -IncludeRoles }
    catch { if ($_.Exception.Message -match 'Retired role') { $blocked = $true } else { throw } }
    if (-not $blocked) { throw 'Installer accepted conflicting retired roles' }
    Write-Host 'Project integration checks passed: policy preservation, no shared copies, repeatability, adaptation detection and retired-role boundary.'
} finally {
    # This exact unique temporary directory is the sole cleanup target.
    $resolvedTestRoot = [IO.Path]::GetFullPath($testRoot)
    $resolvedTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd([IO.Path]::DirectorySeparatorChar)
    if ((Split-Path -Parent $resolvedTestRoot) -ne $resolvedTemp -or
        (Split-Path -Leaf $resolvedTestRoot) -notlike 'codex-workflow-integration-*') {
        throw "Unsafe temporary cleanup path: $resolvedTestRoot"
    }
    Remove-Item -LiteralPath $resolvedTestRoot -Recurse -Force
}
