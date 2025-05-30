# 小型超市零售管理系统 - 后端设计文档

## 1. 系统架构

### 1.1 整体架构

采用经典三层架构设计：
- **表示层**：RESTful API接口，处理HTTP请求和响应
- **业务逻辑层**：实现核心业务逻辑，处理数据验证、业务规则和流程
- **数据访问层**：负责与数据库交互，执行CRUD操作

### 1.2 技术选型

- **开发语言**：Python 3.11
- **Web框架**：Flask
- **ORM框架**：SQLAlchemy
- **数据库**：SQLite（开发环境）/ MySQL（生产环境）
- **认证授权**：JWT (JSON Web Token)
- **API文档**：Swagger/OpenAPI

### 1.3 目录结构

```
backend/
├── app/
│   ├── __init__.py         # 应用初始化
│   ├── config.py           # 配置文件
│   ├── models/             # 数据模型
│   ├── api/                # API路由和控制器
│   ├── services/           # 业务逻辑服务
│   ├── utils/              # 工具函数
│   └── extensions.py       # 扩展插件初始化
├── migrations/             # 数据库迁移文件
├── tests/                  # 测试用例
├── requirements.txt        # 依赖包列表
└── run.py                  # 应用入口
```

## 2. 数据库设计

### 2.1 实体关系图

主要实体：用户(User)、商品(Product)、会员(Member)、订单(Order)、订单项(OrderItem)、库存(Inventory)、进货计划(PurchasePlan)、入库记录(StockIn)

### 2.2 数据表设计

#### 2.2.1 用户表(users)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INTEGER | PRIMARY KEY | 用户ID |
| username | VARCHAR(50) | NOT NULL, UNIQUE | 用户名 |
| password_hash | VARCHAR(128) | NOT NULL | 密码哈希 |
| name | VARCHAR(50) | NOT NULL | 真实姓名 |
| role | VARCHAR(20) | NOT NULL | 角色(admin/cashier) |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### 2.2.2 商品表(products)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INTEGER | PRIMARY KEY | 商品ID |
| code | VARCHAR(50) | NOT NULL, UNIQUE | 商品编号 |
| name | VARCHAR(100) | NOT NULL | 商品名称 |
| barcode | VARCHAR(50) | UNIQUE | 条形码 |
| price | DECIMAL(10,2) | NOT NULL | 单价 |
| status | TINYINT | NOT NULL, DEFAULT 1 | 状态(1:正常,0:下架) |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### 2.2.3 库存表(inventory)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INTEGER | PRIMARY KEY | 库存ID |
| product_id | INTEGER | NOT NULL, FOREIGN KEY | 商品ID |
| quantity | INTEGER | NOT NULL, DEFAULT 0 | 库存数量 |
| alert_threshold | INTEGER | DEFAULT 10 | 库存预警阈值 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### 2.2.4 会员表(members)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INTEGER | PRIMARY KEY | 会员ID |
| card_no | VARCHAR(50) | NOT NULL, UNIQUE | 会员卡号 |
| name | VARCHAR(50) | NOT NULL | 会员姓名 |
| phone | VARCHAR(20) | | 联系方式 |
| join_date | DATE | NOT NULL | 开卡日期 |
| expire_date | DATE | NOT NULL | 到期日期 |
| total_amount | DECIMAL(12,2) | NOT NULL, DEFAULT 0 | 累计消费金额 |
| status | TINYINT | NOT NULL, DEFAULT 1 | 状态(1:有效,0:无效) |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### 2.2.5 订单表(orders)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INTEGER | PRIMARY KEY | 订单ID |
| order_no | VARCHAR(50) | NOT NULL, UNIQUE | 订单编号 |
| user_id | INTEGER | NOT NULL, FOREIGN KEY | 收银员ID |
| member_id | INTEGER | FOREIGN KEY | 会员ID(可为空) |
| total_amount | DECIMAL(12,2) | NOT NULL | 订单总金额 |
| discount_amount | DECIMAL(12,2) | NOT NULL, DEFAULT 0 | 折扣金额 |
| actual_amount | DECIMAL(12,2) | NOT NULL | 实付金额 |
| created_at | DATETIME | NOT NULL | 创建时间 |

#### 2.2.6 订单项表(order_items)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INTEGER | PRIMARY KEY | 订单项ID |
| order_id | INTEGER | NOT NULL, FOREIGN KEY | 订单ID |
| product_id | INTEGER | NOT NULL, FOREIGN KEY | 商品ID |
| quantity | INTEGER | NOT NULL | 数量 |
| price | DECIMAL(10,2) | NOT NULL | 单价 |
| amount | DECIMAL(12,2) | NOT NULL | 小计金额 |

#### 2.2.7 进货计划表(purchase_plans)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INTEGER | PRIMARY KEY | 计划ID |
| plan_no | VARCHAR(50) | NOT NULL, UNIQUE | 计划编号 |
| product_id | INTEGER | NOT NULL, FOREIGN KEY | 商品ID |
| quantity | INTEGER | NOT NULL | 计划数量 |
| status | TINYINT | NOT NULL, DEFAULT 0 | 状态(0:待执行,1:已完成) |
| created_by | INTEGER | NOT NULL, FOREIGN KEY | 创建人ID |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### 2.2.8 入库记录表(stock_in)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INTEGER | PRIMARY KEY | 入库ID |
| stock_in_no | VARCHAR(50) | NOT NULL, UNIQUE | 入库单号 |
| product_id | INTEGER | NOT NULL, FOREIGN KEY | 商品ID |
| quantity | INTEGER | NOT NULL | 入库数量 |
| amount | DECIMAL(12,2) | NOT NULL | 入库金额 |
| plan_id | INTEGER | FOREIGN KEY | 关联计划ID(可为空) |
| created_by | INTEGER | NOT NULL, FOREIGN KEY | 操作人ID |
| created_at | DATETIME | NOT NULL | 创建时间 |

#### 2.2.9 交班记录表(shifts)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INTEGER | PRIMARY KEY | 交班ID |
| user_id | INTEGER | NOT NULL, FOREIGN KEY | 收银员ID |
| start_time | DATETIME | NOT NULL | 开始时间 |
| end_time | DATETIME | | 结束时间 |
| order_count | INTEGER | NOT NULL, DEFAULT 0 | 订单数量 |
| total_amount | DECIMAL(12,2) | NOT NULL, DEFAULT 0 | 总金额 |
| status | TINYINT | NOT NULL, DEFAULT 0 | 状态(0:进行中,1:已结束) |

## 3. API接口设计

### 3.1 认证接口

#### 3.1.1 登录
- **URL**: `/api/auth/login`
- **方法**: POST
- **请求体**:
  ```json
  {
    "username": "admin",
    "password": "password"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "登录成功",
    "data": {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "user": {
        "id": 1,
        "username": "admin",
        "name": "管理员",
        "role": "admin"
      }
    }
  }
  ```

#### 3.1.2 登出
- **URL**: `/api/auth/logout`
- **方法**: POST
- **请求头**: Authorization: Bearer {token}
- **响应**:
  ```json
  {
    "code": 200,
    "message": "登出成功"
  }
  ```

### 3.2 商品接口

#### 3.2.1 添加商品
- **URL**: `/api/products`
- **方法**: POST
- **请求头**: Authorization: Bearer {token}
- **请求体**:
  ```json
  {
    "code": "P001",
    "name": "可口可乐",
    "barcode": "6901234567890",
    "price": 3.5,
    "quantity": 100
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "添加成功",
    "data": {
      "id": 1,
      "code": "P001",
      "name": "可口可乐",
      "barcode": "6901234567890",
      "price": 3.5,
      "status": 1
    }
  }
  ```

#### 3.2.2 获取商品列表
- **URL**: `/api/products`
- **方法**: GET
- **请求头**: Authorization: Bearer {token}
- **查询参数**: page, limit, keyword
- **响应**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "total": 100,
      "items": [
        {
          "id": 1,
          "code": "P001",
          "name": "可口可乐",
          "barcode": "6901234567890",
          "price": 3.5,
          "status": 1,
          "inventory": {
            "quantity": 100,
            "alert_threshold": 10
          }
        }
      ]
    }
  }
  ```

#### 3.2.3 根据条码或编号查询商品
- **URL**: `/api/products/search`
- **方法**: GET
- **请求头**: Authorization: Bearer {token}
- **查询参数**: keyword (条形码或商品编号或名称)
- **响应**:
  ```json
  {
    "code": 200,
    "message": "查询成功",
    "data": {
      "id": 1,
      "code": "P001",
      "name": "可口可乐",
      "barcode": "6901234567890",
      "price": 3.5,
      "status": 1,
      "inventory": {
        "quantity": 100
      }
    }
  }
  ```

### 3.3 会员接口

#### 3.3.1 添加会员
- **URL**: `/api/members`
- **方法**: POST
- **请求头**: Authorization: Bearer {token}
- **请求体**:
  ```json
  {
    "card_no": "M001",
    "name": "张三",
    "phone": "13800138000",
    "join_date": "2023-01-01"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "添加成功",
    "data": {
      "id": 1,
      "card_no": "M001",
      "name": "张三",
      "phone": "13800138000",
      "join_date": "2023-01-01",
      "expire_date": "2024-01-01",
      "status": 1
    }
  }
  ```

#### 3.3.2 获取会员列表
- **URL**: `/api/members`
- **方法**: GET
- **请求头**: Authorization: Bearer {token}
- **查询参数**: page, limit, keyword
- **响应**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "total": 50,
      "items": [
        {
          "id": 1,
          "card_no": "M001",
          "name": "张三",
          "phone": "13800138000",
          "join_date": "2023-01-01",
          "expire_date": "2024-01-01",
          "total_amount": 1000.00,
          "status": 1
        }
      ]
    }
  }
  ```

#### 3.3.3 根据卡号查询会员
- **URL**: `/api/members/search`
- **方法**: GET
- **请求头**: Authorization: Bearer {token}
- **查询参数**: card_no
- **响应**:
  ```json
  {
    "code": 200,
    "message": "查询成功",
    "data": {
      "id": 1,
      "card_no": "M001",
      "name": "张三",
      "phone": "13800138000",
      "join_date": "2023-01-01",
      "expire_date": "2024-01-01",
      "total_amount": 1000.00,
      "status": 1
    }
  }
  ```

### 3.4 销售接口

#### 3.4.1 创建订单
- **URL**: `/api/orders`
- **方法**: POST
- **请求头**: Authorization: Bearer {token}
- **请求体**:
  ```json
  {
    "member_id": 1,  // 可选
    "items": [
      {
        "product_id": 1,
        "quantity": 2,
        "price": 3.5
      }
    ]
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "创建成功",
    "data": {
      "id": 1,
      "order_no": "SO20230101001",
      "user_id": 1,
      "member_id": 1,
      "total_amount": 7.00,
      "discount_amount": 0.35,
      "actual_amount": 6.65,
      "created_at": "2023-01-01 12:00:00",
      "items": [
        {
          "product_id": 1,
          "product_name": "可口可乐",
          "quantity": 2,
          "price": 3.5,
          "amount": 7.00
        }
      ]
    }
  }
  ```

#### 3.4.2 获取订单列表
- **URL**: `/api/orders`
- **方法**: GET
- **请求头**: Authorization: Bearer {token}
- **查询参数**: page, limit, start_date, end_date, user_id
- **响应**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "total": 100,
      "items": [
        {
          "id": 1,
          "order_no": "SO20230101001",
          "user_name": "收银员A",
          "member_name": "张三",
          "total_amount": 7.00,
          "discount_amount": 0.35,
          "actual_amount": 6.65,
          "created_at": "2023-01-01 12:00:00"
        }
      ]
    }
  }
  ```

### 3.5 库存接口

#### 3.5.1 获取库存列表
- **URL**: `/api/inventory`
- **方法**: GET
- **请求头**: Authorization: Bearer {token}
- **查询参数**: page, limit, keyword, alert(0/1)
- **响应**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "total": 100,
      "items": [
        {
          "id": 1,
          "product_id": 1,
          "product_code": "P001",
          "product_name": "可口可乐",
          "quantity": 100,
          "alert_threshold": 10,
          "status": "正常"  // 正常/预警/缺货
        }
      ]
    }
  }
  ```

### 3.6 进货管理接口

#### 3.6.1 创建进货计划
- **URL**: `/api/purchase-plans`
- **方法**: POST
- **请求头**: Authorization: Bearer {token}
- **请求体**:
  ```json
  {
    "product_id": 1,
    "quantity": 50
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "创建成功",
    "data": {
      "id": 1,
      "plan_no": "PP20230101001",
      "product_id": 1,
      "product_name": "可口可乐",
      "quantity": 50,
      "status": 0,
      "created_at": "2023-01-01 12:00:00"
    }
  }
  ```

#### 3.6.2 入库操作
- **URL**: `/api/stock-in`
- **方法**: POST
- **请求头**: Authorization: Bearer {token}
- **请求体**:
  ```json
  {
    "product_id": 1,
    "quantity": 50,
    "amount": 100.00,
    "plan_id": 1  // 可选
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "入库成功",
    "data": {
      "id": 1,
      "stock_in_no": "SI20230101001",
      "product_id": 1,
      "product_name": "可口可乐",
      "quantity": 50,
      "amount": 100.00,
      "created_at": "2023-01-01 12:00:00"
    }
  }
  ```

### 3.7 交班管理接口

#### 3.7.1 开始交班
- **URL**: `/api/shifts/start`
- **方法**: POST
- **请求头**: Authorization: Bearer {token}
- **响应**:
  ```json
  {
    "code": 200,
    "message": "开始交班成功",
    "data": {
      "id": 1,
      "user_id": 1,
      "user_name": "收银员A",
      "start_time": "2023-01-01 08:00:00",
      "status": 0
    }
  }
  ```

#### 3.7.2 结束交班
- **URL**: `/api/shifts/end`
- **方法**: POST
- **请求头**: Authorization: Bearer {token}
- **响应**:
  ```json
  {
    "code": 200,
    "message": "结束交班成功",
    "data": {
      "id": 1,
      "user_id": 1,
      "user_name": "收银员A",
      "start_time": "2023-01-01 08:00:00",
      "end_time": "2023-01-01 17:00:00",
      "order_count": 50,
      "total_amount": 1000.00,
      "status": 1
    }
  }
  ```

### 3.8 统计接口

#### 3.8.1 获取销售统计数据
- **URL**: `/api/stats/sales`
- **方法**: GET
- **请求头**: Authorization: Bearer {token}
- **查询参数**: type(day/week/month), date
- **响应**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "total_amount": 10000.00,
      "order_count": 500,
      "product_count": 1000,
      "member_order_count": 300,
      "details": [
        {
          "date": "2023-01-01",
          "amount": 1000.00,
          "count": 50
        }
      ]
    }
  }
  ```

#### 3.8.2 获取商品销售排行
- **URL**: `/api/stats/products`
- **方法**: GET
- **请求头**: Authorization: Bearer {token}
- **查询参数**: type(day/week/month), date, limit
- **响应**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": [
      {
        "product_id": 1,
        "product_name": "可口可乐",
        "quantity": 500,
        "amount": 1750.00
      }
    ]
  }
  ```

## 4. 业务逻辑实现

### 4.1 用户认证与授权

- 使用JWT进行用户认证
- 基于角色的权限控制(RBAC)
- 密码加密存储(bcrypt)

### 4.2 商品管理

- 商品信息CRUD
- 条形码/编号/名称搜索
- 库存关联管理

### 4.3 会员管理

- 会员信息CRUD
- 会员卡有效期管理
- 会员消费累计

### 4.4 销售管理

- POS收银流程
- 会员折扣计算(95折)
- 订单生成与打印
- 库存自动扣减

### 4.5 库存管理

- 库存预警
- 库存盘点
- 自动生成进货计划

### 4.6 进货管理

- 进货计划生成
- 入库操作
- 库存自动增加

### 4.7 交班管理

- 收银员交班记录
- 销售统计汇总

### 4.8 数据统计

- 销售趋势分析
- 商品销售排行
- 会员消费分析

## 5. 安全性设计

- 密码加密存储
- JWT令牌认证
- 接口权限控制
- 输入数据验证
- 防SQL注入
- 日志记录审计

## 6. 部署方案

### 6.1 开发环境

- 使用SQLite数据库
- 本地开发服务器

### 6.2 生产环境

- 使用MySQL数据库
- Gunicorn + Nginx部署
- 数据定期备份
