from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api_bp
from ..models import Inventory, Product
from ..extensions import db

@api_bp.route('/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    """获取库存列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    keyword = request.args.get('keyword', '')
    alert = request.args.get('alert', type=int)  # 0/1
    
    # 联表查询
    query = db.session.query(Inventory, Product).join(
        Product, Inventory.product_id == Product.id
    )
    
    # 关键字搜索
    if keyword:
        query = query.filter(
            (Product.code.like(f'%{keyword}%')) |
            (Product.name.like(f'%{keyword}%')) |
            (Product.barcode.like(f'%{keyword}%'))
        )
    
    # 库存预警过滤
    if alert == 1:
        query = query.filter(Inventory.quantity <= Inventory.alert_threshold)
    
    # 分页
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    items = pagination.items
    
    inventory_list = []
    for inventory, product in items:
        status = "正常"
        if inventory.quantity <= 0:
            status = "缺货"
        elif inventory.quantity <= inventory.alert_threshold:
            status = "预警"
        
        inventory_data = {
            'id': inventory.id,
            'product_id': product.id,
            'product_code': product.code,
            'product_name': product.name,
            'quantity': inventory.quantity,
            'alert_threshold': inventory.alert_threshold,
            'status': status
        }
        inventory_list.append(inventory_data)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total': pagination.total,
            'items': inventory_list
        }
    })

@api_bp.route('/inventory/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_inventory(product_id):
    """更新库存信息"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '无效的请求数据'}), 400
    
    inventory = Inventory.query.filter_by(product_id=product_id).first()
    if not inventory:
        inventory = Inventory(product_id=product_id)
        db.session.add(inventory)
    
    if 'quantity' in data:
        inventory.quantity = data['quantity']
    if 'alert_threshold' in data:
        inventory.alert_threshold = data['alert_threshold']
    
    db.session.commit()
    
    status = "正常"
    if inventory.quantity <= 0:
        status = "缺货"
    elif inventory.quantity <= inventory.alert_threshold:
        status = "预警"
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': {
            'id': inventory.id,
            'product_id': product.id,
            'product_name': product.name,
            'quantity': inventory.quantity,
            'alert_threshold': inventory.alert_threshold,
            'status': status
        }
    })

@api_bp.route('/inventory/alert', methods=['GET'])
@jwt_required()
def get_inventory_alert():
    """获取库存预警列表"""
    # 联表查询
    query = db.session.query(Inventory, Product).join(
        Product, Inventory.product_id == Product.id
    ).filter(Inventory.quantity <= Inventory.alert_threshold)
    
    items = query.all()
    
    alert_list = []
    for inventory, product in items:
        status = "预警"
        if inventory.quantity <= 0:
            status = "缺货"
        
        alert_data = {
            'id': inventory.id,
            'product_id': product.id,
            'product_code': product.code,
            'product_name': product.name,
            'quantity': inventory.quantity,
            'alert_threshold': inventory.alert_threshold,
            'status': status
        }
        alert_list.append(alert_data)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': alert_list
    })
