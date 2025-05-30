from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from . import api_bp
from ..models import Shift, User, Order
from ..extensions import db

@api_bp.route('/shifts/start', methods=['POST'])
@jwt_required()
def start_shift():
    """开始交班"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'code': 401, 'message': '用户未认证'}), 401
    
    # 检查是否有未结束的交班记录
    active_shift = Shift.query.filter_by(user_id=current_user_id, status=0).first()
    if active_shift:
        return jsonify({'code': 400, 'message': '您有未结束的交班记录，请先结束上一次交班'}), 400
    
    # 创建新的交班记录
    new_shift = Shift(
        user_id=current_user_id,
        start_time=datetime.now(),
        status=0  # 进行中
    )
    
    db.session.add(new_shift)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '开始交班成功',
        'data': {
            'id': new_shift.id,
            'user_id': new_shift.user_id,
            'user_name': user.name,
            'start_time': new_shift.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': new_shift.status
        }
    })

@api_bp.route('/shifts/end', methods=['POST'])
@jwt_required()
def end_shift():
    """结束交班"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'code': 401, 'message': '用户未认证'}), 401
    
    # 查找未结束的交班记录
    active_shift = Shift.query.filter_by(user_id=current_user_id, status=0).first()
    if not active_shift:
        return jsonify({'code': 400, 'message': '没有进行中的交班记录'}), 400
    
    # 计算交班期间的订单数量和总金额
    start_time = active_shift.start_time
    end_time = datetime.now()
    
    orders = Order.query.filter(
        Order.user_id == current_user_id,
        Order.created_at >= start_time,
        Order.created_at <= end_time
    ).all()
    
    order_count = len(orders)
    total_amount = sum(float(order.actual_amount) for order in orders)
    
    # 更新交班记录
    active_shift.end_time = end_time
    active_shift.order_count = order_count
    active_shift.total_amount = total_amount
    active_shift.status = 1  # 已结束
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '结束交班成功',
        'data': {
            'id': active_shift.id,
            'user_id': active_shift.user_id,
            'user_name': user.name,
            'start_time': active_shift.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': active_shift.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'order_count': active_shift.order_count,
            'total_amount': float(active_shift.total_amount),
            'status': active_shift.status
        }
    })

@api_bp.route('/shifts', methods=['GET'])
@jwt_required()
def get_shifts():
    """获取交班记录列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    user_id = request.args.get('user_id', type=int)
    
    query = Shift.query
    
    # 收银员过滤
    if user_id:
        query = query.filter(Shift.user_id == user_id)
    
    # 按开始时间倒序
    query = query.order_by(Shift.start_time.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    shifts = pagination.items
    
    shift_list = []
    for shift in shifts:
        user = User.query.get(shift.user_id)
        
        shift_data = {
            'id': shift.id,
            'user_id': shift.user_id,
            'user_name': user.name if user else '未知',
            'start_time': shift.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': shift.end_time.strftime('%Y-%m-%d %H:%M:%S') if shift.end_time else None,
            'order_count': shift.order_count,
            'total_amount': float(shift.total_amount),
            'status': shift.status
        }
        shift_list.append(shift_data)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total': pagination.total,
            'items': shift_list
        }
    })

@api_bp.route('/shifts/current', methods=['GET'])
@jwt_required()
def get_current_shift():
    """获取当前进行中的交班记录"""
    current_user_id = get_jwt_identity()
    
    active_shift = Shift.query.filter_by(user_id=current_user_id, status=0).first()
    if not active_shift:
        return jsonify({'code': 404, 'message': '没有进行中的交班记录'}), 404
    
    user = User.query.get(active_shift.user_id)
    
    # 计算当前订单数量和总金额
    start_time = active_shift.start_time
    end_time = datetime.now()
    
    orders = Order.query.filter(
        Order.user_id == current_user_id,
        Order.created_at >= start_time,
        Order.created_at <= end_time
    ).all()
    
    order_count = len(orders)
    total_amount = sum(float(order.actual_amount) for order in orders)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'id': active_shift.id,
            'user_id': active_shift.user_id,
            'user_name': user.name if user else '未知',
            'start_time': active_shift.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': int((end_time - active_shift.start_time).total_seconds() / 60),  # 分钟
            'order_count': order_count,
            'total_amount': float(total_amount),
            'status': active_shift.status
        }
    })
