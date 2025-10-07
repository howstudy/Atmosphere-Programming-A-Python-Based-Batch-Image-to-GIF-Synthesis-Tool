@echo off
echo 正在安装GIF制作工具依赖...
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未检测到Python，请先安装Python 3.6或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 检测到Python版本：
python --version
echo.

:: 安装依赖
echo 正在安装依赖包...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo 安装失败，请检查网络连接或手动安装依赖包
    echo 手动安装命令：pip install Pillow numpy
) else (
    echo.
    echo 安装完成！
    echo.
    echo 使用方法：
    echo 1. 双击 start_gui.bat 启动图形界面
    echo 2. 或者运行：python gif_maker.py
    echo 3. 命令行模式：python gif_maker.py --help
)

echo.
pause