# 小型超市零售管理系统 - API文档

## 基础信息

- 基础URL: `http://localhost:5000/api`
- 认证方式: JWT (JSON Web Token)
- 请求头: `Authorization: Bearer {token}`
- 响应格式: JSON

## 通用响应格式

```json
{
  "code": 200,       // 状态码：200成功，4xx客户端错误，5xx服务器错误
  "message": "操作成功", // 响应消息
  "data": {}         // 响应数据，可能是对象或数组
}
```

## 1. 认证接口

### 1.1 登录

- **URL**: `/auth/login`
- **方法**: POST
- **描述**: 用户登录获取令牌
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

### 1.2 登出

- **URL**: `/auth/logout`
- **方法**: POST
- **描述**: 用户登出
- **请求头**: `Authorization: Bearer {token}`
- **响应**:
  ```json
  {
    "code": 200,
    "message": "登出成功"
  }
  ```

### 1.3 注册用户

- **URL**: `/auth/register`
- **方法**: POST
- **描述**: 注册新用户（仅管理员可操作）
- **请求头**: `Authorization: Bearer {token}`
- **请求体**:
  ```json
  {
    "username": "cashier1",
    "password": "password",
    "name": "收银员1",
    "role": "cashier"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "用户创建成功",
    "data": {
      "id": 2,
      "username": "cashier1",
      "name": "收银员1",
      "role": "cashier"
    }
  }
  ```

### 1.4 获取用户列表

- **URL**: `/auth/users`
- **方法**: GET
- **描述**: 获取所有用户（仅管理员可操作）
- **请求头**: `Authorization: Bearer {token}`
- **响应**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": [
      {
        "id": 1,
        "username": "admin",
        "name": "管理员",
        "role": "admin",
        "created_at": "2023-01-01 12:00:00"
      }
    ]
  }
  ```

## 2. 商品接口

### 2.1 添加商品

- **URL**: `/products`
- **方法**: POST
- **描述**: 添加新商品
- **请求头**: `Authorization: Bearer {token}`
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

### 2.2 获取商品列表

- **URL**: `/products`
- **方法**: GET
- **描述**: 获取商品列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码，默认1
  - `limit`: 每页数量，默认10
  - `keyword`: 搜索关键字
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

### 2.3 更新商品

- **URL**: `/products/{product_id}`
- **方法**: PUT
- **描述**: 更新商品信息
- **请求头**: `Authorization: Bearer {token}`
- **请求体**:
  ```json
  {
    "name": "可口可乐(大)",
    "price": 4.5,
    "status": 1,
    "quantity": 50,
    "alert_threshold": 20
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "更新成功",
    "data": {
      "id": 1,
      "code": "P001",
      "name": "可口可乐(大)",
      "barcode": "6901234567890",
      "price": 4.5,
      "status": 1,
      "inventory": {
        "quantity": 50,
        "alert_threshold": 20
      }
    }
  }
  ```

### 2.4 商品搜索

- **URL**: `/products/search`
- **方法**: GET
- **描述**: 根据条码或编号查询商品
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `keyword`: 搜索关键字（条形码/编号/名称）
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

## 3. 会员接口

### 3.1 添加会员

- **URL**: `/members`
- **方法**: POST
- **描述**: 添加新会员
- **请求头**: `Authorization: Bearer {token}`
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

### 3.2 获取会员列表

- **URL**: `/members`
- **方法**: GET
- **描述**: 获取会员列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码，默认1
  - `limit`: 每页数量，默认10
  - `keyword`: 搜索关键字
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

### 3.3 更新会员

- **URL**: `/members/{member_id}`
- **方法**: PUT
- **描述**: 更新会员信息
- **请求头**: `Authorization: Bearer {token}`
- **请求体**:
  ```json
  {
    "name": "张三",
    "phone": "13900139000",
    "status": 1
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "更新成功",
    "data": {
      "id": 1,
      "card_no": "M001",
      "name": "张三",
      "phone": "13900139000",
      "join_date": "2023-01-01",
      "expire_date": "2024-01-01",
      "total_amount": 1000.00,
      "status": 1
    }
  }
  ```

### 3.4 会员搜索

- **URL**: `/members/search`
- **方法**: GET
- **描述**: 根据卡号查询会员
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `card_no`: 会员卡号
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

### 3.5 会员续卡

- **URL**: `/members/renew/{member_id}`
- **方法**: POST
- **描述**: 会员卡续期
- **请求头**: `Authorization: Bearer {token}`
- **响应**:
  ```json
  {
    "code": 200,
    "message": "续卡成功",
    "data": {
      "id": 1,
      "card_no": "M001",
      "name": "张三",
      "expire_date": "2025-01-01",
      "status": 1
    }
  }
  ```

## 4. 库存接口

### 4.1 获取库存列表

- **URL**: `/inventory`
- **方法**: GET
- **描述**: 获取库存列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码，默认1
  - `limit`: 每页数量，默认10
  - `keyword`: 搜索关键字
  - `alert`: 是否只显示预警库存，0/1
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
          "status": "正常"
        }
      ]
    }
  }
  ```

### 4.2 更新库存

- **URL**: `/inventory/{product_id}`
- **方法**: PUT
- **描述**: 更新库存信息
- **请求头**: `Authorization: Bearer {token}`
- **请求体**:
  ```json
  {
    "quantity": 50,
    "alert_threshold": 20
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "更新成功",
    "data": {
      "id": 1,
      "product_id": 1,
      "product_name": "可口可乐",
      "quantity": 50,
      "alert_threshold": 20,
      "status": "正常"
    }
  }
  ```

### 4.3 获取库存预警

- **URL**: `/inventory/alert`
- **方法**: GET
- **描述**: 获取库存预警列表
- **请求头**: `Authorization: Bearer {token}`
- **响应**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": [
      {
        "id": 1,
        "product_id": 1,
        "product_code": "P001",
        "product_name": "可口可乐",
        "quantity": 5,
        "alert_threshold": 10,
        "status": "预警"
      }
    ]
  }
  ```

## 5. 销售接口

### 5.1 创建订单

- **URL**: `/orders`
- **方法**: POST
- **描述**: 创建销售订单
- **请求头**: `Authorization: Bearer {token}`
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

### 5.2 获取订单列表

- **URL**: `/orders`
- **方法**: GET
- **描述**: 获取订单列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码，默认1
  - `limit`: 每页数量，默认10
  - `start_date`: 开始日期，格式YYYY-MM-DD
  - `end_date`: 结束日期，格式YYYY-MM-DD
  - `user_id`: 收银员ID
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

### 5.3 获取订单详情

- **URL**: `/orders/{order_id}`
- **方法**: GET
- **描述**: 获取订单详情
- **请求头**: `Authorization: Bearer {token}`
- **响应**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "id": 1,
      "order_no": "SO20230101001",
      "user_id": 1,
      "user_name": "收银员A",
      "member_id": 1,
      "member_name": "张三",
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

## 6. 进货管理接口

### 6.1 创建进货计划

- **URL**: `/purchase-plans`
- **方法**: POST
- **描述**: 创建进货计划
- **请求头**: `Authorization: Bearer {token}`
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

### 6.2 获取进货计划列表

- **URL**: `/purchase-plans`
- **方法**: GET
- **描述**: 获取进货计划列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码，默认1
  - `limit`: 每页数量，默认10
  - `status`: 状态过滤，0待执行/1已完成
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
          "plan_no": "PP20230101001",
          "product_id": 1,
          "product_name": "可口可乐",
          "quantity": 50,
          "status": 0,
          "created_by": "管理员",
          "created_at": "2023-01-01 12:00:00"
        }
      ]
    }
  }
  ```

### 6.3 入库操作

- **URL**: `/stock-in`
- **方法**: POST
- **描述**: 商品入库
- **请求头**: `Authorization: Bearer {token}`
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

### 6.4 获取入库记录

- **URL**: `/stock-in`
- **方法**: GET
- **描述**: 获取入库记录列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码，默认1
  - `limit`: 每页数量，默认10
  - `start_date`: 开始日期，格式YYYY-MM-DD
  - `end_date`: 结束日期，格式YYYY-MM-DD
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
          "stock_in_no": "SI20230101001",
          "product_id": 1,
          "product_name": "可口可乐",
          "quantity": 50,
          "amount": 100.00,
          "plan_id": 1,
          "created_by": "管理员",
          "created_at": "2023-01-01 12:00:00"
        }
      ]
    }
  }
  ```

## 7. 交班管理接口

### 7.1 开始交班

- **URL**: `/shifts/start`
- **方法**: POST
- **描述**: 开始交班
- **请求头**: `Authorization: Bearer {token}`
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

### 7.2 结束交班

- **URL**: `/shifts/end`
- **方法**: POST
- **描述**: 结束交班
- **请求头**: `Authorization: Bearer {token}`
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

### 7.3 获取交班记录

- **URL**: `/shifts`
- **方法**: GET
- **描述**: 获取交班记录列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码，默认1
  - `limit`: 每页数量，默认10
  - `user_id`: 收银员ID
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
          "user_id": 1,
          "user_name": "收银员A",
          "start_time": "2023-01-01 08:00:00",
          "end_time": "2023-01-01 17:00:00",
          "order_count": 50,
          "total_amount": 1000.00,
          "status": 1
        }
      ]
    }
  }
  ```

### 7.4 获取当前交班

- **URL**: `/shifts/current`
- **方法**: GET
- **描述**: 获取当前进行中的交班记录
- **请求头**: `Authorization: Bearer {token}`
- **响应**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "id": 1,
      "user_id": 1,
      "user_name": "收银员A",
      "start_time": "2023-01-01 08:00:00",
      "duration": 120,  // 分钟
      "order_count": 25,
      "total_amount": 500.00,
      "status": 0
    }
  }
  ```

## 8. 统计接口

### 8.1 销售统计

- **URL**: `/stats/sales`
- **方法**: GET
- **描述**: 获取销售统计数据
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `type`: 统计类型，day/week/month
  - `date`: 日期，格式YYYY-MM-DD
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

### 8.2 商品销售排行

- **URL**: `/stats/products`
- **方法**: GET
- **描述**: 获取商品销售排行
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `type`: 统计类型，day/week/month
  - `date`: 日期，格式YYYY-MM-DD
  - `limit`: 返回数量，默认10
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

### 8.3 仪表盘统计

- **URL**: `/stats/dashboard`
- **方法**: GET
- **描述**: 获取仪表盘统计数据
- **请求头**: `Authorization: Bearer {token}`
- **响应**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "today": {
        "sales": 1000.00,
        "order_count": 50,
        "product_count": 100,
        "member_order_count": 30
      },
      "trend": [
        {
          "date": "05-25",
          "amount": 900.00
        }
      ],
      "category": [
        {
          "name": "可口可乐",
          "amount": 500.00
        }
      ]
    }
  }
  ```

## 错误码说明

- 200: 成功
- 400: 请求参数错误
- 401: 未认证或认证失败
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误

## 注意事项

1. 所有需要认证的接口必须在请求头中携带有效的JWT令牌
2. 部分接口需要管理员权限，普通收银员无法访问
3. 日期格式统一使用YYYY-MM-DD
4. 金额类型在JSON中以浮点数表示
