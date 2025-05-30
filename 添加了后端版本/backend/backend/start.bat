@echo off
chcp 65001
echo 准备启动小型超市零售管理系统后端...

REM 检查是否已安装依赖
if not exist requirements.txt (
    echo 错误：找不到requirements.txt文件，请确保在正确的目录中运行此脚本。
    exit /b 1
)

REM 安装依赖
echo 正在安装依赖...
pip install -r requirements.txt

REM 初始化数据库
echo 正在初始化数据库...
call init_db.bat

REM 启动后端服务
echo 正在启动后端服务...
python run.py

pause 