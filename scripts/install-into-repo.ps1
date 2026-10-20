[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$TargetRepo,
    [switch]$IncludeRoles
)

$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path -Parent $PSScriptRoot
$targetRoot = [IO.Path]::GetFullPath($TargetRepo)
if (-not (Test-Path -LiteralPath $targetRoot -PathType Container)) {
    throw "Target repository does not exist: $targetRoot"
}

# Stage integration assets, never a second edition of shared methods.
function Copy-MissingFile([string]$Source, [string]$Destination) {
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) { throw "Missing source: $Source" }
    if (Test-Path -LiteralPath $Destination) {
        Write-Host "Review existing file: $Destination"
        return
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
    Copy-Item -LiteralPath $Source -Destination $Destination
    Write-Host "Staged: $Destination"
}

if ($IncludeRoles) {
    foreach ($name in @('luna_implementer', 'terra_explorer', 'terra_workhorse', 'terra_reviewer', 'sol_reviewer')) {
        if (Test-Path -LiteralPath (Join-Path $targetRoot ".codex/agents/$name.toml")) {
            throw "Retired role $name exists. Reconcile its references and definition before staging roles."
        }
    }
}
Copy-MissingFile (Join-Path $sourceRoot 'templates/AGENTS-workflow.md') (Join-Path $targetRoot '.codex/AGENTS-workflow.md')
if ($IncludeRoles) {
    foreach ($role in Get-ChildItem -LiteralPath (Join-Path $sourceRoot '.codex/agents') -Filter '*.toml') {
        Copy-MissingFile $role.FullName (Join-Path $targetRoot ".codex/agents/$($role.Name)")
    }
}
Write-Host 'Install/select the shared plugin separately. Use codex-workflow-setup to merge only needed guidance.'
Write-Host 'Roles are staged definitions, not proof of runtime registration. Inspect the diff before use.'
