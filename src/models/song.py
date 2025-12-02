from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from src import db


class Song(db.Model):
    __tablename__ = 'songs'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    is_public = Column(db.Boolean, default=False)

    # content will be a base64 encoded string representing the song file
    content = Column(String, nullable=True)
    lyrics = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships with user that uploaded the song can be added here
    user_id = Column(Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='songs')


    def __repr__(self):
        return self.title

    # CREATE
    @classmethod
    def create(cls, data:dict):
        from src.services.file_service import FileService
        print( data.get('content'))
        content_64 = FileService.file_to_base64(data.get('content'))
        song = cls(
            title=data.get('title'),
            content=content_64,
            is_public=data.get('is_public', False),
            lyrics=data.get('lyrics', ''),
            user_id=data.get('user_id')
        )
        from src import db
        db.session.add(song)
        db.session.commit()
        return song

    # READ
    @classmethod
    def get_by_id(cls, song_id:int):
        from src import db
        return db.session.query(cls).filter_by(id=song_id).first()


    # UPDATE
    @classmethod
    def update(cls, song_id:int, data:dict):
        from src import db
        song = db.session.query(cls).filter_by(id=song_id).first()
        if not song:
            return None
        song.title = data.get('title', song.title)
        song.is_public = data.get('is_public', song.is_public)
        song.lyrics = data.get('lyrics', song.lyrics)
        song.updated_at = datetime.utcnow()
        db.session.commit()
        return song

    # DELETE
    @classmethod
    def delete(cls, song_id:int):
        from src import db
        song = db.session.query(cls).filter_by(id=song_id).first()
        if not song:
            return False
        db.session.delete(song)
        db.session.commit()
        return True
