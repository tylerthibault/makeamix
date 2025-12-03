from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from src import db


# Association table for many-to-many relationship between playlists and songs
playlist_songs = Table('playlist_songs', db.Model.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id'), primary_key=True),
    Column('song_id', Integer, ForeignKey('songs.id'), primary_key=True),
    Column('position', Integer, default=0),  # Track order of songs in playlist
    Column('added_at', DateTime, default=datetime.utcnow)
)


class Playlist(db.Model):
    __tablename__ = 'playlists'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    is_public = Column(db.Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_id = Column(Integer, ForeignKey('users.id'))
    user = db.relationship('User', back_populates='playlists')
    
    # Many-to-many relationship with songs
    songs = db.relationship('Song', secondary=playlist_songs, backref='playlists')

    def __repr__(self):
        return self.name

    # CREATE
    @classmethod
    def create(cls, data: dict):
        playlist = cls(
            name=data.get('name'),
            description=data.get('description', ''),
            is_public=data.get('is_public', False),
            user_id=data.get('user_id')
        )
        db.session.add(playlist)
        db.session.commit()
        return playlist

    # READ
    @classmethod
    def get_by_id(cls, playlist_id: int):
        return db.session.query(cls).filter_by(id=playlist_id).first()

    @classmethod
    def get_by_user(cls, user_id: int):
        return db.session.query(cls).filter_by(user_id=user_id).all()

    @classmethod
    def get_public_playlists(cls):
        return db.session.query(cls).filter_by(is_public=True).all()

    # UPDATE
    @classmethod
    def update(cls, playlist_id: int, data: dict):
        playlist = cls.get_by_id(playlist_id)
        if not playlist:
            return None
        
        playlist.name = data.get('name', playlist.name)
        playlist.description = data.get('description', playlist.description)
        playlist.is_public = data.get('is_public', playlist.is_public)
        playlist.updated_at = datetime.utcnow()
        db.session.commit()
        return playlist

    # DELETE
    @classmethod
    def delete(cls, playlist_id: int):
        playlist = cls.get_by_id(playlist_id)
        if not playlist:
            return False
        db.session.delete(playlist)
        db.session.commit()
        return True

    # Add song to playlist
    def add_song(self, song_id: int):
        from src.models.song import Song
        song = Song.get_by_id(song_id)
        if song and song not in self.songs:
            # Get the current max position
            result = db.session.execute(
                db.select(db.func.max(playlist_songs.c.position))
                .where(playlist_songs.c.playlist_id == self.id)
            ).scalar()
            next_position = (result or -1) + 1
            
            # Insert with position
            db.session.execute(
                playlist_songs.insert().values(
                    playlist_id=self.id,
                    song_id=song_id,
                    position=next_position
                )
            )
            db.session.commit()
            return True
        return False

    # Remove song from playlist
    def remove_song(self, song_id: int):
        from src.models.song import Song
        song = Song.get_by_id(song_id)
        if song and song in self.songs:
            self.songs.remove(song)
            db.session.commit()
            return True
        return False

    # Get songs in order
    def get_ordered_songs(self):
        result = db.session.execute(
            db.select(playlist_songs.c.song_id, playlist_songs.c.position)
            .where(playlist_songs.c.playlist_id == self.id)
            .order_by(playlist_songs.c.position)
        ).all()
        
        from src.models.song import Song
        ordered_songs = []
        for song_id, position in result:
            song = Song.get_by_id(song_id)
            if song:
                ordered_songs.append(song)
        return ordered_songs

    # Reorder songs
    def reorder_songs(self, song_ids: list):
        """Reorder songs based on list of song IDs"""
        for position, song_id in enumerate(song_ids):
            db.session.execute(
                playlist_songs.update()
                .where(
                    (playlist_songs.c.playlist_id == self.id) &
                    (playlist_songs.c.song_id == song_id)
                )
                .values(position=position)
            )
        db.session.commit()
        return True
