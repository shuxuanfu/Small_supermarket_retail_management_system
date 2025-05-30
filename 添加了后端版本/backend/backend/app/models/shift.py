from datetime import datetime
from ..extensions import db

class Shift(db.Model):
    __tablename__ = 'shifts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    order_count = db.Column(db.Integer, default=0, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)  # 0:进行中, 1:已结束
    
    def __repr__(self):
        return f'<Shift user_id={self.user_id}, status={self.status}>'
