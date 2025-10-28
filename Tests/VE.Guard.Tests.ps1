. "$PSScriptRoot\..\ve_kernel.ps1"
Import-Module "$PSScriptRoot\..\Modules\VE.Guard\VE.Guard.psd1" -Force

Describe 'VE Guard' {
  It 'allows Set-Content to ve_data' {
    (Test-VeSafeWrite 'Set-Content -Path ".\ve_data\a.txt" -Value 1') | Should -BeTrue
  }
  It 'blocks absolute path write' {
    (Test-VeSafeWrite 'Set-Content -Path "C:\temp\ve_data\z.txt" -Value 1') | Should -BeFalse
  }
  It 'blocks Out-File redirection' {
    { Assert-VeSafeWrite 'Get-Content a | Out-File ".\ve_data\out.txt"' } | Should -Throw
  }
}
