# Push a file to a GitHub repo via Contents API (base64 body).
param(
  [Parameter(Mandatory=$true)][string]$Repo,
  [Parameter(Mandatory=$true)][string]$Path,
  [Parameter(Mandatory=$true)][string]$LocalFile,
  [Parameter(Mandatory=$true)][string]$Message
)
$sha = gh api "repos/KanakMalpani/$Repo/contents/$Path" --jq .sha 2>$null
$b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes((Get-Content -Raw -Path $LocalFile)))
$body = @{ message = $Message; content = $b64 }
if ($sha) { $body.sha = $sha }
$tmp = [System.IO.Path]::GetTempFileName()
$body | ConvertTo-Json | Set-Content -Path $tmp -Encoding UTF8
gh api -X PUT "repos/KanakMalpani/$Repo/contents/$Path" --input $tmp
Remove-Item $tmp -Force
