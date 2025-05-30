#!/bin/bash

# 启动脚本
# 用于初始化数据库并启动后端服务

echo "准备启动小型超市零售管理系统后端..."

# 检查是否已安装依赖
if [ ! -f "requirements.txt" ]; then
    echo "错误：找不到requirements.txt文件，请确保在正确的目录中运行此脚本。"
    exit 1
fi

# 安装依赖
echo "正在安装依赖..."
pip install -r requirements.txt

# 初始化数据库
echo "正在初始化数据库..."
bash init_db.sh

# 启动后端服务
echo "正在启动后端服务..."
python run.py
