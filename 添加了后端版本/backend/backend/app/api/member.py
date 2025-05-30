from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from . import api_bp
from ..models import Member
from ..extensions import db

@api_bp.route('/members', methods=['POST'])
@jwt_required()
def add_member():
    """添加会员"""
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '无效的请求数据'}), 400
    
    card_no = data.get('card_no')
    name = data.get('name')
    phone = data.get('phone')
    join_date = data.get('join_date')
    
    if not card_no or not name or not join_date:
        return jsonify({'code': 400, 'message': '会员信息不完整'}), 400
    
    # 检查会员卡号是否已存在
    if Member.query.filter_by(card_no=card_no).first():
        return jsonify({'code': 400, 'message': '会员卡号已存在'}), 400
    
    try:
        join_date = datetime.strptime(join_date, '%Y-%m-%d').date()
        expire_date = join_date + timedelta(days=365)  # 有效期一年
    except ValueError:
        return jsonify({'code': 400, 'message': '日期格式错误'}), 400
    
    # 创建新会员
    new_member = Member(
        card_no=card_no,
        name=name,
        phone=phone,
        join_date=join_date,
        expire_date=expire_date
    )
    
    db.session.add(new_member)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '添加成功',
        'data': {
            'id': new_member.id,
            'card_no': new_member.card_no,
            'name': new_member.name,
            'phone': new_member.phone,
            'join_date': new_member.join_date.strftime('%Y-%m-%d'),
            'expire_date': new_member.expire_date.strftime('%Y-%m-%d'),
            'status': new_member.status
        }
    })

@api_bp.route('/members', methods=['GET'])
@jwt_required()
def get_members():
    """获取会员列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    keyword = request.args.get('keyword', '')
    
    query = Member.query
    
    # 关键字搜索
    if keyword:
        query = query.filter(
            (Member.card_no.like(f'%{keyword}%')) |
            (Member.name.like(f'%{keyword}%')) |
            (Member.phone.like(f'%{keyword}%'))
        )
    
    # 分页
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    members = pagination.items
    
    member_list = []
    for member in members:
        member_data = {
            'id': member.id,
            'card_no': member.card_no,
            'name': member.name,
            'phone': member.phone,
            'join_date': member.join_date.strftime('%Y-%m-%d'),
            'expire_date': member.expire_date.strftime('%Y-%m-%d'),
            'total_amount': float(member.total_amount),
            'status': member.status
        }
        member_list.append(member_data)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total': pagination.total,
            'items': member_list
        }
    })

@api_bp.route('/members/<int:member_id>', methods=['PUT'])
@jwt_required()
def update_member(member_id):
    """更新会员信息"""
    member = Member.query.get(member_id)
    if not member:
        return jsonify({'code': 404, 'message': '会员不存在'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '无效的请求数据'}), 400
    
    # 更新会员信息
    if 'name' in data:
        member.name = data['name']
    if 'phone' in data:
        member.phone = data['phone']
    if 'status' in data:
        member.status = data['status']
    if 'expire_date' in data:
        try:
            member.expire_date = datetime.strptime(data['expire_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'code': 400, 'message': '日期格式错误'}), 400
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': {
            'id': member.id,
            'card_no': member.card_no,
            'name': member.name,
            'phone': member.phone,
            'join_date': member.join_date.strftime('%Y-%m-%d'),
            'expire_date': member.expire_date.strftime('%Y-%m-%d'),
            'total_amount': float(member.total_amount),
            'status': member.status
        }
    })

@api_bp.route('/members/search', methods=['GET'])
@jwt_required()
def search_member():
    """根据卡号查询会员"""
    card_no = request.args.get('card_no', '')
    if not card_no:
        return jsonify({'code': 400, 'message': '会员卡号不能为空'}), 400
    
    member = Member.query.filter_by(card_no=card_no).first()
    
    if not member:
        return jsonify({'code': 404, 'message': '会员不存在'}), 404
    
    # 检查会员卡是否有效
    today = datetime.now().date()
    if member.expire_date < today:
        member.status = 0  # 设置为无效
        db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'id': member.id,
            'card_no': member.card_no,
            'name': member.name,
            'phone': member.phone,
            'join_date': member.join_date.strftime('%Y-%m-%d'),
            'expire_date': member.expire_date.strftime('%Y-%m-%d'),
            'total_amount': float(member.total_amount),
            'status': member.status
        }
    })

@api_bp.route('/members/renew/<int:member_id>', methods=['POST'])
@jwt_required()
def renew_member(member_id):
    """续卡"""
    member = Member.query.get(member_id)
    if not member:
        return jsonify({'code': 404, 'message': '会员不存在'}), 404
    
    today = datetime.now().date()
    
    # 如果已过期，从今天开始计算一年
    if member.expire_date < today:
        member.expire_date = today + timedelta(days=365)
    else:
        # 如果未过期，从原到期日开始再延长一年
        member.expire_date = member.expire_date + timedelta(days=365)
    
    member.status = 1  # 设置为有效
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '续卡成功',
        'data': {
            'id': member.id,
            'card_no': member.card_no,
            'name': member.name,
            'expire_date': member.expire_date.strftime('%Y-%m-%d'),
            'status': member.status
        }
    })
