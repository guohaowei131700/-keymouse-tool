@echo off
chcp 65001 >nul
echo ====================================
echo  同步到 GitHub
echo ====================================
echo.
echo.
echo 第一步：上 GitHub 创建空仓库
echo 打开 https://github.com/new
echo 仓库名: keymouse-tool
echo 其他默认，点创建
echo.
echo 第二步：点任意键，自动推送
pause >nul
echo.
git push github master
echo.
if %errorlevel% equ 0 (
    echo 成功推送到 GitHub！
) else (
    echo 推送失败，可能是 GitHub 暂时无法访问，稍后再试
)
echo.
pause
