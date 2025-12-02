from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime
from src import db

class Logbook(db.Model):
    __tablename__ = 'logbook'

    id = Column(Integer, primary_key=True)
    entry = Column(String, nullable=False)
    type = Column(String, nullable=False)
    reference_code = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    hash_key = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # relationships with User
    user_id = Column(Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='log_entries')


    def __repr__(self):
        return f"<Logbook(id={self.id}, entry='{self.entry}', created_at={self.created_at})>"
    

    @classmethod
    def create(cls, data:dict):
        log_entry = cls(
            entry=data.get('entry'),
            type=data.get('type'),
            reference_code=data.get('reference_code'),
            severity=data.get('severity'),
            hash_key=data.get('hash_key', cls.generate_hash()),
            user_id=data.get('user_id')
        )
        from src import db
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    

    @staticmethod
    def generate_hash() -> str:
        import hashlib
        hash_input = f"{datetime.datetime.utcnow().isoformat()}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()
    

    @classmethod
    def get_by_hash(cls, hash_key:str):
        from src import db
        return db.session.query(cls).filter_by(hash_key=hash_key).first()
    
    @classmethod
    def update_updated_at(cls, log_id:int):
        from src import db
        log_entry = db.session.query(cls).filter_by(id=log_id).first()
        if log_entry:
            log_entry.updated_at = datetime.datetime.utcnow()
            db.session.commit()
        return log_entry