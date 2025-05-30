#!/bin/bash

# 系统功能验证脚本
# 用于验证后端API的基本功能

echo "开始验证系统功能..."

# 创建Python脚本
cat > verify_system.py << 'EOF'
import requests
import json
import time
from datetime import datetime

# 基础URL
BASE_URL = "http://localhost:5000/api"
admin_token = None
cashier_token = None

def print_result(title, response):
    """打印响应结果"""
    print(f"\n===== {title} =====")
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"响应内容: {response.text}")

def test_auth():
    """测试认证接口"""
    global admin_token, cashier_token
    
    # 管理员登录
    print("\n\n========== 测试认证接口 ==========")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    print_result("管理员登录", response)
    if response.status_code == 200:
        admin_token = response.json()["data"]["token"]
        print("管理员登录成功，获取token")
    else:
        print("管理员登录失败")
        return False
    
    # 收银员登录
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "cashier",
        "password": "cashier123"
    })
    print_result("收银员登录", response)
    if response.status_code == 200:
        cashier_token = response.json()["data"]["token"]
        print("收银员登录成功，获取token")
    else:
        print("收银员登录失败")
        return False
    
    # 获取用户列表（管理员权限）
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
    print_result("获取用户列表", response)
    
    # 权限测试：收银员尝试获取用户列表
    headers = {"Authorization": f"Bearer {cashier_token}"}
    response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
    print_result("收银员尝试获取用户列表（权限测试）", response)
    
    return True

def test_products():
    """测试商品接口"""
    if not admin_token:
        print("未获取到管理员token，跳过商品接口测试")
        return False
    
    print("\n\n========== 测试商品接口 ==========")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 获取商品列表
    response = requests.get(f"{BASE_URL}/products", headers=headers)
    print_result("获取商品列表", response)
    
    # 添加新商品
    new_product = {
        "code": "P006",
        "name": "雪碧",
        "barcode": "6901234567895",
        "price": 3.5,
        "quantity": 50
    }
    response = requests.post(f"{BASE_URL}/products", headers=headers, json=new_product)
    print_result("添加新商品", response)
    
    if response.status_code == 200:
        product_id = response.json()["data"]["id"]
        
        # 更新商品
        update_data = {
            "name": "雪碧(大瓶)",
            "price": 4.0,
            "quantity": 60
        }
        response = requests.put(f"{BASE_URL}/products/{product_id}", headers=headers, json=update_data)
        print_result("更新商品", response)
        
        # 商品搜索
        response = requests.get(f"{BASE_URL}/products/search?keyword=雪碧", headers=headers)
        print_result("商品搜索", response)
    
    return True

def test_members():
    """测试会员接口"""
    if not admin_token:
        print("未获取到管理员token，跳过会员接口测试")
        return False
    
    print("\n\n========== 测试会员接口 ==========")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 获取会员列表
    response = requests.get(f"{BASE_URL}/members", headers=headers)
    print_result("获取会员列表", response)
    
    # 添加新会员
    today = datetime.now().strftime("%Y-%m-%d")
    new_member = {
        "card_no": "M003",
        "name": "王五",
        "phone": "13800138002",
        "join_date": today
    }
    response = requests.post(f"{BASE_URL}/members", headers=headers, json=new_member)
    print_result("添加新会员", response)
    
    if response.status_code == 200:
        member_id = response.json()["data"]["id"]
        
        # 更新会员
        update_data = {
            "name": "王五",
            "phone": "13900139002"
        }
        response = requests.put(f"{BASE_URL}/members/{member_id}", headers=headers, json=update_data)
        print_result("更新会员", response)
        
        # 会员搜索
        response = requests.get(f"{BASE_URL}/members/search?card_no=M003", headers=headers)
        print_result("会员搜索", response)
        
        # 会员续卡
        response = requests.post(f"{BASE_URL}/members/renew/{member_id}", headers=headers)
        print_result("会员续卡", response)
    
    return True

def test_inventory():
    """测试库存接口"""
    if not admin_token:
        print("未获取到管理员token，跳过库存接口测试")
        return False
    
    print("\n\n========== 测试库存接口 ==========")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 获取库存列表
    response = requests.get(f"{BASE_URL}/inventory", headers=headers)
    print_result("获取库存列表", response)
    
    # 获取库存预警
    response = requests.get(f"{BASE_URL}/inventory/alert", headers=headers)
    print_result("获取库存预警", response)
    
    # 更新库存
    if response.status_code == 200 and response.json()["data"]["items"]:
        product_id = response.json()["data"]["items"][0]["product_id"]
        update_data = {
            "quantity": 200,
            "alert_threshold": 30
        }
        response = requests.put(f"{BASE_URL}/inventory/{product_id}", headers=headers, json=update_data)
        print_result("更新库存", response)
    
    return True

def test_orders():
    """测试订单接口"""
    if not cashier_token:
        print("未获取到收银员token，跳过订单接口测试")
        return False
    
    print("\n\n========== 测试订单接口 ==========")
    headers = {"Authorization": f"Bearer {cashier_token}"}
    
    # 获取商品列表
    response = requests.get(f"{BASE_URL}/products", headers=headers)
    if response.status_code != 200 or not response.json()["data"]["items"]:
        print("获取商品失败，跳过订单测试")
        return False
    
    product = response.json()["data"]["items"][0]
    product_id = product["id"]
    price = product["price"]
    
    # 创建普通订单
    order_data = {
        "items": [
            {
                "product_id": product_id,
                "quantity": 2,
                "price": price
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/orders", headers=headers, json=order_data)
    print_result("创建普通订单", response)
    
    # 获取会员列表
    response = requests.get(f"{BASE_URL}/members", headers=headers)
    if response.status_code == 200 and response.json()["data"]["items"]:
        member_id = response.json()["data"]["items"][0]["id"]
        
        # 创建会员订单
        order_data = {
            "member_id": member_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 3,
                    "price": price
                }
            ]
        }
        response = requests.post(f"{BASE_URL}/orders", headers=headers, json=order_data)
        print_result("创建会员订单", response)
    
    # 获取订单列表
    response = requests.get(f"{BASE_URL}/orders", headers=headers)
    print_result("获取订单列表", response)
    
    # 获取订单详情
    if response.status_code == 200 and response.json()["data"]["items"]:
        order_id = response.json()["data"]["items"][0]["id"]
        response = requests.get(f"{BASE_URL}/orders/{order_id}", headers=headers)
        print_result("获取订单详情", response)
    
    return True

def test_purchase():
    """测试进货接口"""
    if not admin_token:
        print("未获取到管理员token，跳过进货接口测试")
        return False
    
    print("\n\n========== 测试进货接口 ==========")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 获取商品列表
    response = requests.get(f"{BASE_URL}/products", headers=headers)
    if response.status_code != 200 or not response.json()["data"]["items"]:
        print("获取商品失败，跳过进货测试")
        return False
    
    product_id = response.json()["data"]["items"][0]["id"]
    
    # 创建进货计划
    plan_data = {
        "product_id": product_id,
        "quantity": 50
    }
    response = requests.post(f"{BASE_URL}/purchase-plans", headers=headers, json=plan_data)
    print_result("创建进货计划", response)
    
    # 获取进货计划列表
    response = requests.get(f"{BASE_URL}/purchase-plans", headers=headers)
    print_result("获取进货计划列表", response)
    
    # 入库操作
    if response.status_code == 200 and response.json()["data"]["items"]:
        plan_id = response.json()["data"]["items"][0]["id"]
        stock_in_data = {
            "product_id": product_id,
            "quantity": 50,
            "amount": 100.00,
            "plan_id": plan_id
        }
        response = requests.post(f"{BASE_URL}/stock-in", headers=headers, json=stock_in_data)
        print_result("入库操作", response)
    
    # 获取入库记录列表
    response = requests.get(f"{BASE_URL}/stock-in", headers=headers)
    print_result("获取入库记录列表", response)
    
    return True

def test_shifts():
    """测试交班接口"""
    if not cashier_token:
        print("未获取到收银员token，跳过交班接口测试")
        return False
    
    print("\n\n========== 测试交班接口 ==========")
    headers = {"Authorization": f"Bearer {cashier_token}"}
    
    # 开始交班
    response = requests.post(f"{BASE_URL}/shifts/start", headers=headers)
    print_result("开始交班", response)
    
    # 获取当前交班
    response = requests.get(f"{BASE_URL}/shifts/current", headers=headers)
    print_result("获取当前交班", response)
    
    # 结束交班
    response = requests.post(f"{BASE_URL}/shifts/end", headers=headers)
    print_result("结束交班", response)
    
    # 获取交班记录列表
    response = requests.get(f"{BASE_URL}/shifts", headers=headers)
    print_result("获取交班记录列表", response)
    
    return True

def test_stats():
    """测试统计接口"""
    if not admin_token:
        print("未获取到管理员token，跳过统计接口测试")
        return False
    
    print("\n\n========== 测试统计接口 ==========")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 获取销售统计
    today = datetime.now().strftime("%Y-%m-%d")
    response = requests.get(f"{BASE_URL}/stats/sales?type=day&date={today}", headers=headers)
    print_result("获取销售统计", response)
    
    # 获取商品销售排行
    response = requests.get(f"{BASE_URL}/stats/products?type=day&date={today}&limit=5", headers=headers)
    print_result("获取商品销售排行", response)
    
    # 获取仪表盘统计
    response = requests.get(f"{BASE_URL}/stats/dashboard", headers=headers)
    print_result("获取仪表盘统计", response)
    
    return True

def main():
    """主函数"""
    print("开始系统功能验证...")
    
    # 等待服务启动
    print("等待后端服务启动...")
    time.sleep(2)
    
    # 测试认证接口
    if not test_auth():
        print("认证接口测试失败，终止验证")
        return
    
    # 测试商品接口
    test_products()
    
    # 测试会员接口
    test_members()
    
    # 测试库存接口
    test_inventory()
    
    # 测试订单接口
    test_orders()
    
    # 测试进货接口
    test_purchase()
    
    # 测试交班接口
    test_shifts()
    
    # 测试统计接口
    test_stats()
    
    print("\n\n系统功能验证完成！")

if __name__ == "__main__":
    main()
EOF

echo "验证脚本已创建，请先启动后端服务，然后运行以下命令进行验证："
echo "python3 verify_system.py"
echo ""
echo "注意：验证前请确保后端服务已启动，并且已执行init_db.sh初始化数据库"
