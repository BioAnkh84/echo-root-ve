# VE.Guard.psm1 — Trust-gated write guard (PS 5.1-safe)
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

# Put options on ONE line to avoid '-bor' at the start of a line
$VE_RegexOptions = [Text.RegularExpressions.RegexOptions]::IgnoreCase -bor [Text.RegularExpressions.RegexOptions]::IgnorePatternWhitespace -bor [Text.RegularExpressions.RegexOptions]::Compiled

$VE_Allow = [regex]::new($VE_PatternAllow, $VE_RegexOptions, [TimeSpan]::FromMilliseconds(50))

function Test-VeSafeWrite {
  param([Parameter(Mandatory)][string]$Command)
  $VE_Allow.IsMatch($Command)
}

function Assert-VeSafeWrite {
  param([Parameter(Mandatory)][string]$Command)
  if ($Command -match '(?<!\S)(?:\d?>|>>)|\bOut-File\b') { throw 'VE GUARD: redirection/Out-File not allowed; use Set-Content/Add-Content into .\ve_data\.' }
  if ($Command -match '\s--%\s') { throw 'VE GUARD: --% stop-parsing not allowed.' }
  if (-not (Test-VeSafeWrite $Command)) { throw "VE GUARD: blocked write; only Set-Content/Add-Content to '.\ve_data\' is allowed. Command: $Command" }
}

Export-ModuleMember -Function Test-VeSafeWrite, Assert-VeSafeWrite