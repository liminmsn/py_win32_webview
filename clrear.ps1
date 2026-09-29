# 清理旧产物
Remove-Item -Path "F:\python\win32\dist","F:\python\win32\build" -Recurse -Force -ErrorAction SilentlyContinue;
Write-Host "已清理 dist 和 build 目录" -ForegroundColor Green;
Start-Sleep -Seconds 1
