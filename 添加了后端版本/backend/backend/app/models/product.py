from datetime import datetime
from ..extensions import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    barcode = db.Column(db.String(50), unique=True)
    category = db.Column(db.String(50))
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.Integer, default=1, nullable=False)  # 1:正常, 0:下架
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # 关联
    inventory = db.relationship('Inventory', backref='product', uselist=False, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    purchase_plans = db.relationship('PurchasePlan', backref='product', lazy='dynamic')
    stock_ins = db.relationship('StockIn', backref='product', lazy='dynamic')
    
    def __repr__(self):
        return f'<Product {self.name}>'
