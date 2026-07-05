[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$url = "https://github.com/donothingday/setup-helper/releases/latest/download/setup-helper.exe"
$out = "$env:TEMP\setup-helper.exe"

Write-Host "Downloading Setup Helper..."
Invoke-WebRequest -Uri $url -OutFile $out

Write-Host "Running..."
Start-Process -FilePath $out -Wait
