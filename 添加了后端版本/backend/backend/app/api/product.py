from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api_bp
from ..models import Product, Inventory
from ..extensions import db

@api_bp.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    """添加商品"""
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '无效的请求数据'}), 400
    
    code = data.get('code')
    name = data.get('name')
    barcode = data.get('barcode')
    price = data.get('price')
    quantity = data.get('quantity', 0)
    
    if not code or not name or not price:
        return jsonify({'code': 400, 'message': '商品信息不完整'}), 400
    
    # 检查商品编号是否已存在
    if Product.query.filter_by(code=code).first():
        return jsonify({'code': 400, 'message': '商品编号已存在'}), 400
    
    # 检查条形码是否已存在（如果提供了条形码）
    if barcode and Product.query.filter_by(barcode=barcode).first():
        return jsonify({'code': 400, 'message': '条形码已存在'}), 400
    
    # 创建新商品
    new_product = Product(
        code=code,
        name=name,
        barcode=barcode,
        price=price
    )
    
    db.session.add(new_product)
    db.session.flush()  # 获取新商品ID
    
    # 创建库存记录
    inventory = Inventory(
        product_id=new_product.id,
        quantity=quantity
    )
    
    db.session.add(inventory)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '添加成功',
        'data': {
            'id': new_product.id,
            'code': new_product.code,
            'name': new_product.name,
            'barcode': new_product.barcode,
            'price': float(new_product.price),
            'status': new_product.status
        }
    })

@api_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    """获取商品列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    keyword = request.args.get('keyword', '')
    
    query = Product.query
    
    # 关键字搜索
    if keyword:
        query = query.filter(
            (Product.code.like(f'%{keyword}%')) |
            (Product.name.like(f'%{keyword}%')) |
            (Product.barcode.like(f'%{keyword}%'))
        )
    
    # 分页
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    products = pagination.items
    
    product_list = []
    for product in products:
        product_data = {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'barcode': product.barcode,
            'price': float(product.price),
            'status': product.status,
            'inventory': {
                'quantity': product.inventory.quantity if product.inventory else 0,
                'alert_threshold': product.inventory.alert_threshold if product.inventory else 10
            }
        }
        product_list.append(product_data)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total': pagination.total,
            'items': product_list
        }
    })

@api_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """更新商品信息"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '无效的请求数据'}), 400
    
    # 更新商品信息
    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'status' in data:
        product.status = data['status']
    if 'barcode' in data:
        # 检查条形码是否已存在
        if data['barcode'] and data['barcode'] != product.barcode and Product.query.filter_by(barcode=data['barcode']).first():
            return jsonify({'code': 400, 'message': '条形码已存在'}), 400
        product.barcode = data['barcode']
    
    # 更新库存信息
    if 'quantity' in data or 'alert_threshold' in data:
        inventory = product.inventory
        if not inventory:
            inventory = Inventory(product_id=product.id)
            db.session.add(inventory)
        
        if 'quantity' in data:
            inventory.quantity = data['quantity']
        if 'alert_threshold' in data:
            inventory.alert_threshold = data['alert_threshold']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'barcode': product.barcode,
            'price': float(product.price),
            'status': product.status,
            'inventory': {
                'quantity': product.inventory.quantity if product.inventory else 0,
                'alert_threshold': product.inventory.alert_threshold if product.inventory else 10
            }
        }
    })

@api_bp.route('/products/search', methods=['GET'])
@jwt_required()
def search_product():
    """根据条码或编号查询商品"""
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({'code': 400, 'message': '搜索关键字不能为空'}), 400
    
    product = Product.query.filter(
        (Product.code == keyword) |
        (Product.barcode == keyword) |
        (Product.name.like(f'%{keyword}%'))
    ).first()
    
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    
    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'barcode': product.barcode,
            'price': float(product.price),
            'status': product.status,
            'inventory': {
                'quantity': product.inventory.quantity if product.inventory else 0
            }
        }
    })
