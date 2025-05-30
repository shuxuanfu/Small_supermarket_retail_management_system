from flask import Flask, send_from_directory, request, Response, send_file
from app import create_app
import os

app = create_app()

# 获取项目根目录的绝对路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONT_DIR = os.path.abspath(os.path.join(BASE_DIR, '../../front'))

print(f"BASE_DIR: {BASE_DIR}")
print(f"FRONT_DIR: {FRONT_DIR}")
print(f"Login page path: {os.path.join(FRONT_DIR, 'page/login.html')}")

# 检查文件是否存在
login_path = os.path.join(FRONT_DIR, 'page/login.html')
if os.path.exists(login_path):
    print(f"Login page exists at: {login_path}")
else:
    print(f"Login page NOT found at: {login_path}")

# 添加静态文件路由
@app.route('/')
def index():
    try:
        print(f"Attempting to serve login page from: {login_path}")
        return send_file(login_path)
    except Exception as e:
        print(f"Error serving login page: {str(e)}")
        return str(e), 500

@app.route('/<path:path>')
def serve_page(path):
    try:
        if path.startswith('api/'):
            # 将请求转发到API蓝图
            from app.api import api_bp
            # 移除api前缀
            path = path[4:]
            # 转发请求
            with app.request_context(request.environ):
                return api_bp.dispatch_request()
        
        # 处理静态文件
        if path.startswith('css/'):
            file_path = os.path.join(FRONT_DIR, path)
        elif path.startswith('js/'):
            file_path = os.path.join(FRONT_DIR, path)
        elif path.startswith('img/'):
            file_path = os.path.join(FRONT_DIR, path)
        else:
            # 其他路径都当作页面处理
            file_path = os.path.join(FRONT_DIR, 'page', path)
        
        print(f"Serving file: {file_path}")
        return send_file(file_path)
    except Exception as e:
        print(f"Error serving file {path}: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 