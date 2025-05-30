from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import bcrypt
from . import api_bp
from ..models import User
from ..extensions import db

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '无效的请求数据'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
    
    # 创建访问令牌
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'role': user.role
            }
        }
    })

@api_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出接口"""
    # JWT无状态，客户端只需删除token即可，这里仅作为API规范提供
    return jsonify({'code': 200, 'message': '登出成功'})

@api_bp.route('/auth/register', methods=['POST'])
@jwt_required()
def register():
    """注册新用户（仅管理员可操作）"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 检查权限
    if not current_user or current_user.role != 'admin':
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '无效的请求数据'}), 400
    
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', 'cashier')
    
    if not username or not password or not name:
        return jsonify({'code': 400, 'message': '用户信息不完整'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400
    
    # 创建新用户
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(
        username=username,
        password_hash=hashed_password,
        name=name,
        role=role
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '用户创建成功',
        'data': {
            'id': new_user.id,
            'username': new_user.username,
            'name': new_user.name,
            'role': new_user.role
        }
    })

@api_bp.route('/auth/users', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表（仅管理员可操作）"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 检查权限
    if not current_user or current_user.role != 'admin':
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    users = User.query.all()
    user_list = [{
        'id': user.id,
        'username': user.username,
        'name': user.name,
        'role': user.role,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for user in users]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': user_list
    })
