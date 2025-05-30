from datetime import datetime
from ..extensions import db

class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    card_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    join_date = db.Column(db.Date, nullable=False)
    expire_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    status = db.Column(db.Integer, default=1, nullable=False)  # 1:有效, 0:无效
    points = db.Column(db.Integer, default=0, nullable=False)  # 新增字段，积分
    level = db.Column(db.String(20), default='普通会员', nullable=False)  # 新增字段，会员等级
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # 关联
    orders = db.relationship('Order', backref='member', lazy='dynamic')
    
    def __repr__(self):
        return f'<Member {self.name}>'
