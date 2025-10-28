param([string]$Version = "1.20.1")
$api = "https://api.papermc.io/v2/projects/paper/versions/$Version"
Write-Host "[*] Fetching latest build for Paper $Version ..."
$resp = Invoke-RestMethod -Uri $api
$build = $resp.builds[-1]
$url = "https://api.papermc.io/v2/projects/paper/versions/$Version/builds/$build/downloads/paper-$Version-$build.jar"
Write-Host "[*] Download: $url"
Invoke-WebRequest -Uri $url -OutFile "paper.jar"
Write-Host "[*] Done. Run .\start.bat"
