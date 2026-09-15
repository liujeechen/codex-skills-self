[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,

    [Parameter(Mandatory = $true)]
    [string]$Path,

    [Parameter(Mandatory = $true)]
    [string]$PlaintextPath
)

$ErrorActionPreference = 'Stop'

function Invoke-GitText {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)

    $output = & git -C $script:Repository @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed:`n$($output -join "`n")"
    }
    return ($output -join "`n").TrimEnd()
}

$resolvedInputRoot = [IO.Path]::GetFullPath($RepoRoot)
$Repository = $resolvedInputRoot
$Repository = [IO.Path]::GetFullPath((Invoke-GitText -Arguments @('rev-parse', '--show-toplevel')).Trim())
if ($Repository.TrimEnd('\') -ne $resolvedInputRoot.TrimEnd('\')) {
    throw "RepoRoot is not the repository top level: $RepoRoot (actual: $Repository)"
}

$plainFile = [IO.Path]::GetFullPath($PlaintextPath)
if (-not [IO.File]::Exists($plainFile)) {
    throw "Plaintext file does not exist: $plainFile"
}

$relativePath = $Path.Replace('\', '/').TrimStart('/')
if ([string]::IsNullOrWhiteSpace($relativePath) -or $relativePath.Contains('..')) {
    throw "Unsafe repository-relative path: $Path"
}

$targetFullPath = [IO.Path]::GetFullPath((Join-Path $Repository $relativePath))
$repoPrefix = $Repository.TrimEnd('\') + '\'
if (-not $targetFullPath.StartsWith($repoPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Target resolves outside repository: $targetFullPath"
}

$indexLine = Invoke-GitText -Arguments @('ls-files', '--stage', '--', $relativePath)
if ($indexLine -notmatch '^([0-9]{6}) ([0-9a-fA-F]{40,64}) 0\t(.+)$') {
    throw "Target must be a tracked stage-zero regular entry: $relativePath"
}
$mode = $Matches[1]
if ($mode -notin @('100644', '100755')) {
    throw "Unsupported target mode $mode for $relativePath"
}

$realIndex = Join-Path $Repository '.git\index'
if (-not [IO.File]::Exists($realIndex)) {
    throw "Real Git index not found: $realIndex"
}
$indexHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $realIndex).Hash
$temporaryIndex = Join-Path ([IO.Path]::GetTempPath()) ("tsd-index-" + [Guid]::NewGuid().ToString('N'))
$previousIndexEnvironment = $env:GIT_INDEX_FILE

try {
    $blobHash = (& git -C $Repository hash-object -w --no-filters -- $plainFile).Trim()
    if ($LASTEXITCODE -ne 0 -or $blobHash -notmatch '^[0-9a-fA-F]{40,64}$') {
        throw 'Failed to create plaintext Git blob.'
    }

    [IO.File]::Copy($realIndex, $temporaryIndex, $false)
    $env:GIT_INDEX_FILE = $temporaryIndex

    & git -C $Repository update-index --cacheinfo "$mode,$blobHash,$relativePath"
    if ($LASTEXITCODE -ne 0) {
        throw 'Failed to update temporary Git index.'
    }

    & git -C $Repository checkout-index -f -- $relativePath
    if ($LASTEXITCODE -ne 0) {
        throw 'Failed to recreate protected worktree file through checkout-index.'
    }
}
finally {
    if ($null -eq $previousIndexEnvironment) {
        Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue
    }
    else {
        $env:GIT_INDEX_FILE = $previousIndexEnvironment
    }
    if ([IO.File]::Exists($temporaryIndex)) {
        [IO.File]::Delete($temporaryIndex)
    }
}

$indexHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $realIndex).Hash
if ($indexHashAfter -ne $indexHashBefore) {
    throw 'The real Git index changed unexpectedly; inspect the repository before continuing.'
}

& git -C $Repository diff --check -- $relativePath
if ($LASTEXITCODE -ne 0) {
    throw "Installed file failed git diff --check: $relativePath"
}

Write-Output "Installed plaintext through Git/TSD filters without staging: $relativePath"
