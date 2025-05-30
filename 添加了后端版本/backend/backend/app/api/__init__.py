from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from functools import wraps

api_bp = Blueprint('api', __name__)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        from ..models import User
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return jsonify({'code': 403, 'message': '权限不足'}), 403
        return fn(*args, **kwargs)
    return wrapper

# 添加API根路由
@api_bp.route('/')
def index():
    return jsonify({
        'message': 'API服务正常运行',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/auth',
            'products': '/products',
            'members': '/members',
            'orders': '/orders',
            'inventory': '/inventory',
            'stats': '/stats'
        }
    })

# 导入各模块路由
from . import auth, product, member, inventory, order, purchase, shift, stats
