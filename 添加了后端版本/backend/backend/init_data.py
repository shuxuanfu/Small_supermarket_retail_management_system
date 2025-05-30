from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.member import Member
from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.models.purchase import PurchasePlan
from app.models.shift import Shift
import bcrypt
from datetime import datetime, timedelta

def init_data():
    app = create_app()
    with app.app_context():
        # 清空现有数据
        db.drop_all()
        db.create_all()
        
        # 创建管理员用户
        admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        admin = User(
            username='admin',
            password_hash=admin_password.decode('utf-8'),
            role='admin',
            name='系统管理员'
        )
        db.session.add(admin)
        
        # 创建普通用户
        staff_password = bcrypt.hashpw('staff123'.encode('utf-8'), bcrypt.gensalt())
        staff = User(
            username='staff',
            password_hash=staff_password.decode('utf-8'),
            role='staff',
            name='收银员'
        )
        db.session.add(staff)
        
        # 创建商品
        products = [
            Product(
                code='P001',
                name='可口可乐',
                barcode='6901234567890',
                category='饮料',
                price=3.50,
                status=1
            ),
            Product(
                code='P002',
                name='百事可乐',
                barcode='6901234567891',
                category='饮料',
                price=3.50,
                status=1
            ),
            Product(
                code='P003',
                name='康师傅方便面',
                barcode='6901234567892',
                category='食品',
                price=4.50,
                status=1
            ),
            Product(
                code='P004',
                name='农夫山泉',
                barcode='6901234567893',
                category='饮料',
                price=2.00,
                status=1
            ),
            Product(
                code='P005',
                name='乐事薯片',
                barcode='6901234567894',
                category='零食',
                price=6.50,
                status=1
            ),
            Product(
                code='P006',
                name='红牛',
                barcode='6901234567895',
                category='饮料',
                price=6.00,
                status=1
            ),
            Product(
                code='P007',
                name='王老吉',
                barcode='6901234567896',
                category='饮料',
                price=4.50,
                status=1
            ),
            Product(
                code='P008',
                name='统一冰红茶',
                barcode='6901234567897',
                category='饮料',
                price=3.00,
                status=1
            ),
            Product(
                code='P009',
                name='好丽友派',
                barcode='6901234567898',
                category='零食',
                price=8.50,
                status=1
            ),
            Product(
                code='P010',
                name='奥利奥',
                barcode='6901234567899',
                category='零食',
                price=7.50,
                status=1
            ),
            Product(
                code='P011',
                name='卫龙辣条',
                barcode='6901234567900',
                category='零食',
                price=2.50,
                status=1
            ),
            Product(
                code='P012',
                name='蒙牛纯牛奶',
                barcode='6901234567901',
                category='乳制品',
                price=5.50,
                status=1
            ),
            Product(
                code='P013',
                name='伊利酸奶',
                barcode='6901234567902',
                category='乳制品',
                price=4.50,
                status=1
            ),
            Product(
                code='P014',
                name='统一老坛酸菜面',
                barcode='6901234567903',
                category='食品',
                price=4.50,
                status=1
            ),
            Product(
                code='P015',
                name='康师傅红烧牛肉面',
                barcode='6901234567904',
                category='食品',
                price=4.50,
                status=1
            )
        ]
        for product in products:
            db.session.add(product)
        
        # 提交商品数据以获取ID
        db.session.commit()
        
        # 创建库存记录
        for product in products:
            inventory = Inventory(
                product_id=product.id,
                quantity=100,
                alert_threshold=10,
                updated_at=datetime.now()
            )
            db.session.add(inventory)
        
        # 创建会员
        members = [
            Member(
                card_no='M001',
                name='张三',
                phone='13800138001',
                join_date=datetime.now().date(),
                expire_date=(datetime.now() + timedelta(days=365)).date(),
                points=100,
                level='普通会员'
            ),
            Member(
                card_no='M002',
                name='李四',
                phone='13800138002',
                join_date=datetime.now().date(),
                expire_date=(datetime.now() + timedelta(days=365)).date(),
                points=500,
                level='银卡会员'
            ),
            Member(
                card_no='M003',
                name='王五',
                phone='13800138003',
                join_date=datetime.now().date(),
                expire_date=(datetime.now() + timedelta(days=365)).date(),
                points=1000,
                level='金卡会员'
            )
        ]
        for member in members:
            db.session.add(member)
        
        # 创建班次记录
        shifts = [
            Shift(
                user_id=staff.id,
                start_time=datetime.now() - timedelta(hours=8),
                end_time=datetime.now(),
                status='completed'
            ),
            Shift(
                user_id=staff.id,
                start_time=datetime.now(),
                end_time=None,
                status='active'
            )
        ]
        for shift in shifts:
            db.session.add(shift)
        
        # 创建订单
        order = Order(
            order_no='O202403150001',
            member_id=members[0].id,
            user_id=staff.id,
            total_amount=10.50,
            discount_amount=0.00,
            actual_amount=10.50,
            payment_method='现金',
            status='completed',
            created_at=datetime.now()
        )
        db.session.add(order)
        
        # 提交订单数据以获取ID
        db.session.commit()
        
        # 创建订单项
        order_items = [
            OrderItem(
                order_id=order.id,
                product_id=products[0].id,
                quantity=2,
                price=products[0].price,
                subtotal=products[0].price * 2
            ),
            OrderItem(
                order_id=order.id,
                product_id=products[3].id,
                quantity=1,
                price=products[3].price,
                subtotal=products[3].price
            )
        ]
        for item in order_items:
            db.session.add(item)
        
        # 创建采购计划
        purchase_plan = PurchasePlan(
            plan_no='P202403150001',
            product_id=products[0].id,
            quantity=50,
            status=1,
            created_by=admin.id,
            created_at=datetime.now()
        )
        db.session.add(purchase_plan)
        
        # 提交所有更改
        db.session.commit()
        print('测试数据初始化完成！')

if __name__ == '__main__':
    init_data() 