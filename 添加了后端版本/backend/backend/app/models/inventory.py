from datetime import datetime
from ..extensions import db

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    alert_threshold = db.Column(db.Integer, default=10)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def __repr__(self):
        return f'<Inventory product_id={self.product_id}, quantity={self.quantity}>'
