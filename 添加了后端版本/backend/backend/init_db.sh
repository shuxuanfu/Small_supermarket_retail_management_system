#!/bin/bash

# 初始化数据库脚本
# 用于创建初始用户和测试数据

echo "开始初始化数据库..."

# 创建Python脚本
cat > init_db.py << 'EOF'
from app import create_app
from app.extensions import db
from app.models import User, Product, Member, Inventory
import bcrypt
from datetime import datetime, timedelta

def init_db():
    """初始化数据库，创建表和初始数据"""
    app = create_app('development')
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已有管理员用户
        if User.query.filter_by(username='admin').first() is None:
            # 创建管理员用户
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = User(
                username='admin',
                password_hash=hashed_password,
                name='系统管理员',
                role='admin'
            )
            db.session.add(admin)
            
            # 创建收银员用户
            hashed_password = bcrypt.hashpw('cashier123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cashier = User(
                username='cashier',
                password_hash=hashed_password,
                name='收银员',
                role='cashier'
            )
            db.session.add(cashier)
            
            # 创建示例商品
            products = [
                {'code': 'P001', 'name': '可口可乐', 'barcode': '6901234567890', 'price': 3.5, 'quantity': 100},
                {'code': 'P002', 'name': '百事可乐', 'barcode': '6901234567891', 'price': 3.5, 'quantity': 80},
                {'code': 'P003', 'name': '农夫山泉', 'barcode': '6901234567892', 'price': 2.0, 'quantity': 150},
                {'code': 'P004', 'name': '康师傅方便面', 'barcode': '6901234567893', 'price': 4.5, 'quantity': 60},
                {'code': 'P005', 'name': '乐事薯片', 'barcode': '6901234567894', 'price': 6.0, 'quantity': 40}
            ]
            
            for p in products:
                product = Product(
                    code=p['code'],
                    name=p['name'],
                    barcode=p['barcode'],
                    price=p['price']
                )
                db.session.add(product)
                db.session.flush()  # 获取新商品ID
                
                # 创建库存
                inventory = Inventory(
                    product_id=product.id,
                    quantity=p['quantity']
                )
                db.session.add(inventory)
            
            # 创建示例会员
            today = datetime.now().date()
            members = [
                {'card_no': 'M001', 'name': '张三', 'phone': '13800138000', 'join_date': today, 'expire_date': today + timedelta(days=365)},
                {'card_no': 'M002', 'name': '李四', 'phone': '13800138001', 'join_date': today, 'expire_date': today + timedelta(days=365)}
            ]
            
            for m in members:
                member = Member(
                    card_no=m['card_no'],
                    name=m['name'],
                    phone=m['phone'],
                    join_date=m['join_date'],
                    expire_date=m['expire_date']
                )
                db.session.add(member)
            
            db.session.commit()
            print("数据库初始化完成！")
        else:
            print("数据库已初始化，无需重复操作。")

if __name__ == '__main__':
    init_db()
EOF

# 执行Python脚本
cd /home/ubuntu/project/backend
python3 init_db.py

echo "数据库初始化完成！"
echo "管理员账号: admin / admin123"
echo "收银员账号: cashier / cashier123"
