# 清理旧产物
Remove-Item -Path "F:\python\win32\dist","F:\python\win32\build" -Recurse -Force -ErrorAction SilentlyContinue;
Write-Host "已清理 dist 和 build 目录，1 秒后开始打包..." -ForegroundColor Green;
Start-Sleep -Seconds 1

# 打包
.\.venv\Scripts\python.exe -m PyInstaller main.spec --clean --noconfirm

# 打包完成后提示
if ($LASTEXITCODE -eq 0) {
    Write-Host "打包完成：F:\python\win32\dist\WinView2App\WinView2App.exe" -ForegroundColor Cyan
} else {
    Write-Host "打包失败，退出码：$LASTEXITCODE" -ForegroundColor Red
}