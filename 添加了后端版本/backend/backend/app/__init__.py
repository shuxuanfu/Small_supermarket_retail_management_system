import os
from flask import Flask, jsonify
from flask_cors import CORS
from .extensions import db, migrate, jwt
from .config import config

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    CORS(app, resources={r"/*": {"origins": "*"}})
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 注册蓝图
    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 添加健康检查路由
    @app.route('/health')
    def health_check():
        try:
            # 尝试执行一个简单的数据库查询来检查连接
            db.session.execute('SELECT 1')
            db_status = 'connected'
        except Exception as e:
            db_status = 'error'
            
        return jsonify({
            'status': 'healthy',
            'database': db_status
        })
    
    return app
