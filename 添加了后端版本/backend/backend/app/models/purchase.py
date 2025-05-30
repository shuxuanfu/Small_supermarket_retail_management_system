from datetime import datetime
from ..extensions import db

class PurchasePlan(db.Model):
    __tablename__ = 'purchase_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_no = db.Column(db.String(50), unique=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)  # 0:待执行, 1:已完成
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # 关联
    stock_ins = db.relationship('StockIn', backref='plan', lazy='dynamic')
    
    def __repr__(self):
        return f'<PurchasePlan {self.plan_no}>'

class StockIn(db.Model):
    __tablename__ = 'stock_in'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_in_no = db.Column(db.String(50), unique=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('purchase_plans.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    def __repr__(self):
        return f'<StockIn {self.stock_in_no}>'
