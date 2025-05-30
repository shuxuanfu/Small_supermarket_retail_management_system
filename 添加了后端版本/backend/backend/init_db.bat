@echo off
chcp 65001
echo 正在初始化数据库...

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请确保已安装Python并添加到系统环境变量中。
    exit /b 1
)

REM 检查Flask环境
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Flask，请先运行 pip install -r requirements.txt
    exit /b 1
)

REM 初始化数据库
echo 正在创建数据库表...
python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"

REM 导入初始数据
echo 正在导入初始数据...
python init_data.py

echo 数据库初始化完成！ 