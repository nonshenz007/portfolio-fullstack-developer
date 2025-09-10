from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
import json

db = SQLAlchemy()

class BaseModel(db.Model):
    """Base model with common fields and methods"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[c.name] = value
        return result
    
    def generate_hash(self):
        """Generate SHA-256 hash of the model data"""
        data_str = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    @classmethod
    def get_or_create(cls, **kwargs):
        """Get existing record or create new one"""
        instance = cls.query.filter_by(**kwargs).first()
        if instance:
            return instance, False
        else:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance, True