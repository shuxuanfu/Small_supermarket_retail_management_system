from datetime import datetime
from ..extensions import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin/cashier
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # 关联
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    shifts = db.relationship('Shift', backref='user', lazy='dynamic')
    purchase_plans = db.relationship('PurchasePlan', backref='creator', lazy='dynamic')
    stock_ins = db.relationship('StockIn', backref='operator', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
