from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
import secrets
import string

from src import db


class Song(db.Model):
    __tablename__ = 'songs'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    is_public = Column(db.Boolean, default=False)

    # short_id is a unique identifier for URL/filename generation
    short_id = Column(String(12), unique=True, nullable=False)
    # file_path stores the relative path to the audio file
    file_path = Column(String(500), nullable=True)
    lyrics = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships with user that uploaded the song can be added here
    user_id = Column(Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='songs')


    def __repr__(self):
        return self.title
    
    @staticmethod
    def generate_short_id():
        """Generate a unique 12-character alphanumeric ID"""
        alphabet = string.ascii_lowercase + string.digits
        while True:
            short_id = ''.join(secrets.choice(alphabet) for _ in range(12))
            # Check if this ID already exists
            if not db.session.query(Song).filter_by(short_id=short_id).first():
                return short_id

    # CREATE
    @classmethod
    def create(cls, data:dict):
        from src.services.file_service import FileService
        
        # Generate unique short_id
        short_id = cls.generate_short_id()
        
        # Save file to filesystem
        file_obj = data.get('content')
        file_path = None
        if file_obj:
            file_path = FileService.save_song_file(
                file_obj=file_obj,
                user_id=data.get('user_id'),
                short_id=short_id
            )
        
        song = cls(
            title=data.get('title'),
            short_id=short_id,
            file_path=file_path,
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
        from src.services.file_service import FileService
        
        song = db.session.query(cls).filter_by(id=song_id).first()
        if not song:
            return False
        
        # Delete the file from filesystem
        if song.file_path:
            FileService.delete_song_file(song.file_path)
        
        db.session.delete(song)
        db.session.commit()
        return True
