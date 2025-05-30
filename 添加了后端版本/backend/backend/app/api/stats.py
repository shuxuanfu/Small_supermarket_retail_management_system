from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func
from . import api_bp
from ..models import Order, OrderItem, Product, Member, User

@api_bp.route('/stats/sales', methods=['GET'])
@jwt_required()
def get_sales_stats():
    """获取销售统计数据"""
    type_param = request.args.get('type', 'day')  # day/week/month
    date_param = request.args.get('date')
    
    # 默认为今天
    if not date_param:
        date_param = datetime.now().strftime('%Y-%m-%d')
    
    try:
        target_date = datetime.strptime(date_param, '%Y-%m-%d')
    except ValueError:
        return jsonify({'code': 400, 'message': '日期格式错误'}), 400
    
    # 根据类型确定日期范围
    if type_param == 'day':
        start_date = target_date.replace(hour=0, minute=0, second=0)
        end_date = target_date.replace(hour=23, minute=59, second=59)
    elif type_param == 'week':
        # 获取本周的星期一
        start_date = target_date - timedelta(days=target_date.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date = start_date + timedelta(days=6)
        end_date = end_date.replace(hour=23, minute=59, second=59)
    elif type_param == 'month':
        # 获取本月第一天
        start_date = target_date.replace(day=1, hour=0, minute=0, second=0)
        # 获取下个月第一天，然后减去1秒
        if target_date.month == 12:
            end_date = datetime(target_date.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(target_date.year, target_date.month + 1, 1) - timedelta(seconds=1)
    else:
        return jsonify({'code': 400, 'message': '类型参数错误'}), 400
    
    # 查询订单数据
    orders = Order.query.filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).all()
    
    # 计算统计数据
    total_amount = sum(float(order.actual_amount) for order in orders)
    order_count = len(orders)
    
    # 计算商品总数
    product_count = 0
    for order in orders:
        product_count += sum(item.quantity for item in order.items)
    
    # 计算会员订单数
    member_order_count = sum(1 for order in orders if order.member_id is not None)
    
    # 按日期分组统计
    details = []
    if type_param == 'day':
        # 按小时统计
        for hour in range(24):
            hour_start = start_date.replace(hour=hour, minute=0, second=0)
            hour_end = start_date.replace(hour=hour, minute=59, second=59)
            
            hour_orders = [order for order in orders if hour_start <= order.created_at <= hour_end]
            hour_amount = sum(float(order.actual_amount) for order in hour_orders)
            
            details.append({
                'date': f"{hour:02d}:00",
                'amount': hour_amount,
                'count': len(hour_orders)
            })
    elif type_param == 'week':
        # 按天统计
        for day in range(7):
            day_date = start_date + timedelta(days=day)
            day_start = day_date.replace(hour=0, minute=0, second=0)
            day_end = day_date.replace(hour=23, minute=59, second=59)
            
            day_orders = [order for order in orders if day_start <= order.created_at <= day_end]
            day_amount = sum(float(order.actual_amount) for order in day_orders)
            
            details.append({
                'date': day_date.strftime('%Y-%m-%d'),
                'amount': day_amount,
                'count': len(day_orders)
            })
    elif type_param == 'month':
        # 按天统计
        days_in_month = (end_date - start_date).days + 1
        for day in range(days_in_month):
            day_date = start_date + timedelta(days=day)
            day_start = day_date.replace(hour=0, minute=0, second=0)
            day_end = day_date.replace(hour=23, minute=59, second=59)
            
            day_orders = [order for order in orders if day_start <= order.created_at <= day_end]
            day_amount = sum(float(order.actual_amount) for order in day_orders)
            
            details.append({
                'date': day_date.strftime('%Y-%m-%d'),
                'amount': day_amount,
                'count': len(day_orders)
            })
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total_amount': total_amount,
            'order_count': order_count,
            'product_count': product_count,
            'member_order_count': member_order_count,
            'details': details
        }
    })

@api_bp.route('/stats/products', methods=['GET'])
@jwt_required()
def get_product_stats():
    """获取商品销售排行"""
    type_param = request.args.get('type', 'day')  # day/week/month
    date_param = request.args.get('date')
    limit = request.args.get('limit', 10, type=int)
    
    # 默认为今天
    if not date_param:
        date_param = datetime.now().strftime('%Y-%m-%d')
    
    try:
        target_date = datetime.strptime(date_param, '%Y-%m-%d')
    except ValueError:
        return jsonify({'code': 400, 'message': '日期格式错误'}), 400
    
    # 根据类型确定日期范围
    if type_param == 'day':
        start_date = target_date.replace(hour=0, minute=0, second=0)
        end_date = target_date.replace(hour=23, minute=59, second=59)
    elif type_param == 'week':
        # 获取本周的星期一
        start_date = target_date - timedelta(days=target_date.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date = start_date + timedelta(days=6)
        end_date = end_date.replace(hour=23, minute=59, second=59)
    elif type_param == 'month':
        # 获取本月第一天
        start_date = target_date.replace(day=1, hour=0, minute=0, second=0)
        # 获取下个月第一天，然后减去1秒
        if target_date.month == 12:
            end_date = datetime(target_date.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(target_date.year, target_date.month + 1, 1) - timedelta(seconds=1)
    else:
        return jsonify({'code': 400, 'message': '类型参数错误'}), 400
    
    # 查询订单项数据
    orders = Order.query.filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).all()
    
    # 统计商品销售情况
    product_stats = {}
    for order in orders:
        for item in order.items:
            if item.product_id not in product_stats:
                product = Product.query.get(item.product_id)
                product_stats[item.product_id] = {
                    'product_id': item.product_id,
                    'product_name': product.name if product else '未知商品',
                    'quantity': 0,
                    'amount': 0
                }
            
            product_stats[item.product_id]['quantity'] += item.quantity
            product_stats[item.product_id]['amount'] += float(item.amount)
    
    # 排序并限制数量
    sorted_stats = sorted(
        product_stats.values(),
        key=lambda x: x['amount'],
        reverse=True
    )[:limit]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': sorted_stats
    })

@api_bp.route('/stats/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """获取仪表盘统计数据"""
    # 获取今日日期
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # 获取今日销售数据
    today_orders = Order.query.filter(
        Order.created_at >= today_start,
        Order.created_at <= today_end
    ).all()
    
    today_sales = sum(float(order.actual_amount) for order in today_orders)
    today_order_count = len(today_orders)
    
    # 计算今日销售商品数量
    today_product_count = 0
    for order in today_orders:
        today_product_count += sum(item.quantity for item in order.items)
    
    # 计算今日会员订单数
    today_member_order_count = sum(1 for order in today_orders if order.member_id is not None)
    
    # 获取7天销售趋势
    seven_days_ago = today - timedelta(days=6)
    seven_days_start = datetime.combine(seven_days_ago, datetime.min.time())
    
    seven_days_trend = []
    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        day_orders = Order.query.filter(
            Order.created_at >= day_start,
            Order.created_at <= day_end
        ).all()
        
        day_sales = sum(float(order.actual_amount) for order in day_orders)
        
        seven_days_trend.append({
            'date': day.strftime('%m-%d'),
            'amount': day_sales
        })
    
    # 获取商品分类占比（这里简化为按商品统计）
    all_orders = Order.query.filter(
        Order.created_at >= seven_days_start,
        Order.created_at <= today_end
    ).all()
    
    product_stats = {}
    for order in all_orders:
        for item in order.items:
            if item.product_id not in product_stats:
                product = Product.query.get(item.product_id)
                product_stats[item.product_id] = {
                    'name': product.name if product else '未知商品',
                    'amount': 0
                }
            
            product_stats[item.product_id]['amount'] += float(item.amount)
    
    # 取销售额前5的商品
    top_products = sorted(
        product_stats.values(),
        key=lambda x: x['amount'],
        reverse=True
    )[:5]
    
    # 计算其他商品的总销售额
    other_amount = sum(item['amount'] for item in list(product_stats.values())[5:]) if len(product_stats) > 5 else 0
    
    # 如果有其他商品，添加到列表中
    if other_amount > 0:
        top_products.append({
            'name': '其他',
            'amount': other_amount
        })
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'today': {
                'sales': today_sales,
                'order_count': today_order_count,
                'product_count': today_product_count,
                'member_order_count': today_member_order_count
            },
            'trend': seven_days_trend,
            'category': top_products
        }
    })
