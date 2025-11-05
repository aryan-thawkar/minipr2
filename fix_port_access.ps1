# This script must be run as Administrator
$port = "COM7"

Write-Host "Stopping any processes that might be using $port..."
Get-Process | Where-Object { $_.Name -like "*python*" -or $_.Name -like "*serial*" } | Stop-Process -Force

Write-Host "Releasing $port..."
Remove-Item -Path "\\.\$port" -ErrorAction SilentlyContinue

Write-Host "Configuring $port..."
mode $port BAUD=9600 PARITY=n DATA=8 STOP=1 TO=on DTR=on RTS=on

Write-Host "Setting permissions..."
$acl = Get-Acl "\\.\$port"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone","FullControl","Allow")
$acl.SetAccessRule($rule)
$acl | Set-Acl "\\.\$port"

Write-Host "Done! You should now be able to access $port"