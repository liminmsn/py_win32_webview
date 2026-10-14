# 找 signtool 和 makeappx
$sdkBin = (Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin" -Recurse -Filter signtool.exe -ErrorAction SilentlyContinue |
    Where-Object FullName -match '\\x64\\' | Select-Object -Last 1).DirectoryName

$signtool = Join-Path $sdkBin "signtool.exe"
$makeappx = Join-Path $sdkBin "makeappx.exe"

$signtool
$makeappx

# 注意前面的 & 符号
& $signtool sign `
  /fd SHA256 `
  /f "C:\dev\hkhj5_test.pfx" `
  /p "123456" `
  /tr http://timestamp.digicert.com `
  /td SHA256 `
  "F:\python\win32\appx\hkhj5.msix"