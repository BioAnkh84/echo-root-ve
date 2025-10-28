# ve_guard.ps1 — allow Set-Content/Add-Content only to .\ve_data\...

$VE_PatternAllow = @'
(?xi)
^ \s*
(?:Set-Content|Add-Content)
\s+ -(?:Path|LiteralPath) \s+
(?:"|')?
\.\\ve_data\\
(?:[^"'\r\n\\]+\\)*
[^"'\r\n\\]+
(?:"|')?
(?=\s|$)
'@

$VE_RegexOptions = [Text.RegularExpressions.RegexOptions]::IgnoreCase `
                 -bor [Text.RegularExpressions.RegexOptions]::IgnorePatternWhitespace `
                 -bor [Text.RegularExpressions.RegexOptions]::Compiled

$VE_Allow = [regex]::new($VE_PatternAllow, $VE_RegexOptions, [TimeSpan]::FromMilliseconds(50))

function Test-VeSafeWrite {
    param([Parameter(Mandatory)][string]$Command)
    $VE_Allow.IsMatch($Command)
}

function Assert-VeSafeWrite {
    param([Parameter(Mandatory)][string]$Command)
    if (-not (Test-VeSafeWrite $Command)) {
        throw "VE GUARD: blocked write; only Set-Content/Add-Content to '.\ve_data\' is allowed. Command: $Command"
    }
}

if ($MyInvocation.MyCommand.Module) {
    Export-ModuleMember -Function Test-VeSafeWrite, Assert-VeSafeWrite
}
