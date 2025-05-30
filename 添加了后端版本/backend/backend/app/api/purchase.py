from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid
from . import api_bp
from ..models import PurchasePlan, StockIn, Product, Inventory, User
from ..extensions import db

@api_bp.route('/purchase-plans', methods=['POST'])
@jwt_required()
def create_purchase_plan():
    """创建进货计划"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'code': 401, 'message': '用户未认证'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '无效的请求数据'}), 400
    
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    if not product_id or not quantity:
        return jsonify({'code': 400, 'message': '计划信息不完整'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    
    # 生成计划编号
    plan_no = f"PP{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4().int)[:6]}"
    
    # 创建进货计划
    new_plan = PurchasePlan(
        plan_no=plan_no,
        product_id=product_id,
        quantity=quantity,
        created_by=current_user_id
    )
    
    db.session.add(new_plan)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': {
            'id': new_plan.id,
            'plan_no': new_plan.plan_no,
            'product_id': new_plan.product_id,
            'product_name': product.name,
            'quantity': new_plan.quantity,
            'status': new_plan.status,
            'created_at': new_plan.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@api_bp.route('/purchase-plans', methods=['GET'])
@jwt_required()
def get_purchase_plans():
    """获取进货计划列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    status = request.args.get('status', type=int)  # 0:待执行, 1:已完成
    
    query = PurchasePlan.query
    
    # 状态过滤
    if status is not None:
        query = query.filter(PurchasePlan.status == status)
    
    # 按创建时间倒序
    query = query.order_by(PurchasePlan.created_at.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    plans = pagination.items
    
    plan_list = []
    for plan in plans:
        product = Product.query.get(plan.product_id)
        user = User.query.get(plan.created_by)
        
        plan_data = {
            'id': plan.id,
            'plan_no': plan.plan_no,
            'product_id': plan.product_id,
            'product_name': product.name if product else '未知商品',
            'quantity': plan.quantity,
            'status': plan.status,
            'created_by': user.name if user else '未知',
            'created_at': plan.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        plan_list.append(plan_data)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total': pagination.total,
            'items': plan_list
        }
    })

@api_bp.route('/stock-in', methods=['POST'])
@jwt_required()
def create_stock_in():
    """入库操作"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'code': 401, 'message': '用户未认证'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '无效的请求数据'}), 400
    
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    amount = data.get('amount')
    plan_id = data.get('plan_id')
    
    if not product_id or not quantity or not amount:
        return jsonify({'code': 400, 'message': '入库信息不完整'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    
    # 检查关联的进货计划
    plan = None
    if plan_id:
        plan = PurchasePlan.query.get(plan_id)
        if not plan:
            return jsonify({'code': 404, 'message': '进货计划不存在'}), 404
        
        # 更新计划状态
        plan.status = 1  # 已完成
    
    # 生成入库单号
    stock_in_no = f"SI{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4().int)[:6]}"
    
    # 创建入库记录
    new_stock_in = StockIn(
        stock_in_no=stock_in_no,
        product_id=product_id,
        quantity=quantity,
        amount=amount,
        plan_id=plan_id,
        created_by=current_user_id
    )
    
    db.session.add(new_stock_in)
    
    # 更新库存
    inventory = Inventory.query.filter_by(product_id=product_id).first()
    if not inventory:
        inventory = Inventory(product_id=product_id, quantity=0)
        db.session.add(inventory)
    
    inventory.quantity += quantity
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '入库成功',
        'data': {
            'id': new_stock_in.id,
            'stock_in_no': new_stock_in.stock_in_no,
            'product_id': new_stock_in.product_id,
            'product_name': product.name,
            'quantity': new_stock_in.quantity,
            'amount': float(new_stock_in.amount),
            'created_at': new_stock_in.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@api_bp.route('/stock-in', methods=['GET'])
@jwt_required()
def get_stock_in_records():
    """获取入库记录列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = StockIn.query
    
    # 日期过滤
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(StockIn.created_at >= start_datetime)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            query = query.filter(StockIn.created_at <= end_datetime)
        except ValueError:
            pass
    
    # 按创建时间倒序
    query = query.order_by(StockIn.created_at.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    records = pagination.items
    
    record_list = []
    for record in records:
        product = Product.query.get(record.product_id)
        user = User.query.get(record.created_by)
        
        record_data = {
            'id': record.id,
            'stock_in_no': record.stock_in_no,
            'product_id': record.product_id,
            'product_name': product.name if product else '未知商品',
            'quantity': record.quantity,
            'amount': float(record.amount),
            'plan_id': record.plan_id,
            'created_by': user.name if user else '未知',
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        record_list.append(record_data)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total': pagination.total,
            'items': record_list
        }
    })
