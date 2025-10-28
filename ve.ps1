param([Parameter(ValueFromRemainingArguments=\True)] [string[]]\)
. "$PSScriptRoot\ve_kernel.ps1"
Import-Module "$PSScriptRoot\Modules\VE.Guard\VE.Guard.psd1" -Force
\ = \ -join ' '
Invoke-Child \