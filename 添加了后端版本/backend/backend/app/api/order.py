from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid
from . import api_bp
from ..models import Order, OrderItem, Product, Member, Inventory, User
from ..extensions import db

@api_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    """创建订单"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'code': 401, 'message': '用户未认证'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '无效的请求数据'}), 400
    
    member_id = data.get('member_id')
    items = data.get('items', [])
    
    if not items:
        return jsonify({'code': 400, 'message': '订单项不能为空'}), 400
    
    # 生成订单编号
    order_no = f"SO{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4().int)[:6]}"
    
    # 计算订单金额
    total_amount = 0
    discount_amount = 0
    order_items = []
    
    # 验证会员
    member = None
    if member_id:
        member = Member.query.get(member_id)
        if not member:
            return jsonify({'code': 400, 'message': '会员不存在'}), 400
        
        # 检查会员卡是否有效
        today = datetime.now().date()
        if member.expire_date < today or member.status == 0:
            return jsonify({'code': 400, 'message': '会员卡已过期或无效'}), 400
    
    # 处理订单项
    for item_data in items:
        product_id = item_data.get('product_id')
        quantity = item_data.get('quantity')
        price = item_data.get('price')
        
        if not product_id or not quantity or not price:
            return jsonify({'code': 400, 'message': '订单项数据不完整'}), 400
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'code': 400, 'message': f'商品ID {product_id} 不存在'}), 400
        
        # 检查库存
        inventory = Inventory.query.filter_by(product_id=product_id).first()
        if not inventory or inventory.quantity < quantity:
            return jsonify({'code': 400, 'message': f'商品 {product.name} 库存不足'}), 400
        
        # 计算金额
        amount = float(price) * quantity
        total_amount += amount
        
        # 创建订单项
        order_item = OrderItem(
            product_id=product_id,
            quantity=quantity,
            price=price,
            amount=amount
        )
        order_items.append(order_item)
        
        # 减少库存
        inventory.quantity -= quantity
    
    # 计算会员折扣
    actual_amount = total_amount
    if member:
        discount_amount = total_amount * 0.05  # 95折，折扣5%
        actual_amount = total_amount - discount_amount
        
        # 更新会员累计消费金额
        member.total_amount += actual_amount
    
    # 创建订单
    new_order = Order(
        order_no=order_no,
        user_id=current_user_id,
        member_id=member_id,
        total_amount=total_amount,
        discount_amount=discount_amount,
        actual_amount=actual_amount
    )
    
    # 添加订单项
    for item in order_items:
        new_order.items.append(item)
    
    db.session.add(new_order)
    db.session.commit()
    
    # 准备响应数据
    items_data = []
    for item in new_order.items:
        product = Product.query.get(item.product_id)
        items_data.append({
            'product_id': item.product_id,
            'product_name': product.name,
            'quantity': item.quantity,
            'price': float(item.price),
            'amount': float(item.amount)
        })
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': {
            'id': new_order.id,
            'order_no': new_order.order_no,
            'user_id': new_order.user_id,
            'member_id': new_order.member_id,
            'total_amount': float(new_order.total_amount),
            'discount_amount': float(new_order.discount_amount),
            'actual_amount': float(new_order.actual_amount),
            'created_at': new_order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': items_data
        }
    })

@api_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """获取订单列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_id = request.args.get('user_id', type=int)
    
    query = Order.query
    
    # 日期过滤
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Order.created_at >= start_datetime)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            query = query.filter(Order.created_at <= end_datetime)
        except ValueError:
            pass
    
    # 收银员过滤
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    # 按时间倒序
    query = query.order_by(Order.created_at.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    orders = pagination.items
    
    order_list = []
    for order in orders:
        user = User.query.get(order.user_id)
        member_name = None
        if order.member_id:
            member = Member.query.get(order.member_id)
            if member:
                member_name = member.name
        
        order_data = {
            'id': order.id,
            'order_no': order.order_no,
            'user_name': user.name if user else '未知',
            'member_name': member_name,
            'total_amount': float(order.total_amount),
            'discount_amount': float(order.discount_amount),
            'actual_amount': float(order.actual_amount),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        order_list.append(order_data)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total': pagination.total,
            'items': order_list
        }
    })

@api_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):
    """获取订单详情"""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    user = User.query.get(order.user_id)
    member_name = None
    if order.member_id:
        member = Member.query.get(order.member_id)
        if member:
            member_name = member.name
    
    items_data = []
    for item in order.items:
        product = Product.query.get(item.product_id)
        items_data.append({
            'product_id': item.product_id,
            'product_name': product.name if product else '未知商品',
            'quantity': item.quantity,
            'price': float(item.price),
            'amount': float(item.amount)
        })
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'id': order.id,
            'order_no': order.order_no,
            'user_id': order.user_id,
            'user_name': user.name if user else '未知',
            'member_id': order.member_id,
            'member_name': member_name,
            'total_amount': float(order.total_amount),
            'discount_amount': float(order.discount_amount),
            'actual_amount': float(order.actual_amount),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': items_data
        }
    })
