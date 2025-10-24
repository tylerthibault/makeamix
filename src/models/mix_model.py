"""
This module defines the Mix and Song models for the music application.
It includes a many-to-many relationship between mixes and songs, allowing
songs to belong to multiple mixes and mixes to contain multiple songs.
"""
from datetime import datetime
from src import db


# Association table for many-to-many relationship between mixes and songs
mix_songs = db.Table('mix_songs',
    db.Column('mix_id', db.Integer, db.ForeignKey('mixes.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id'), primary_key=True),
    db.Column('track_number', db.Integer, nullable=True),
    db.Column('added_at', db.DateTime, default=datetime.utcnow)
)


class Mix(db.Model):
    """Mix model for music collections."""
    
    __tablename__ = 'mixes'
    
    # Primary key and timestamps
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Mix information
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    genre = db.Column(db.String(50), index=True)
    
    # Mix metadata
    cover_image = db.Column(db.String(255))  # Path to cover image file
    visibility = db.Column(db.String(20), default='private', nullable=False)  # private, class, public
    
    # Statistics
    play_count = db.Column(db.Integer, default=0, nullable=False)
    like_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Relationships
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by = db.relationship('User', backref=db.backref('mixes', lazy=True))
    
    # Many-to-many relationship with songs
    songs = db.relationship('Song', secondary=mix_songs, lazy='subquery',
                           backref=db.backref('mixes', lazy=True))
    
    def __repr__(self):
        return f'<Mix {self.title}>'
    
    @classmethod
    def create_new_mix(cls, title, description, genre, visibility, created_by_id):
        """Factory method to create and save a new mix."""
        mix = cls(
            title=title,
            description=description,
            genre=genre,
            visibility=visibility,
            created_by_id=created_by_id
        )
        
        db.session.add(mix)
        db.session.commit()
        
        return mix
    
    @property
    def song_count(self):
        """Get the number of songs in this mix."""
        return len(self.songs)
    
    @property
    def total_duration(self):
        """Calculate total duration of all songs in the mix."""
        total_seconds = sum(song.duration_seconds or 0 for song in self.songs)
        if total_seconds == 0:
            return "0:00"
        
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def get_songs_ordered(self):
        """Get songs ordered by track number."""
        # Get songs with their track numbers from the association table
        query = db.session.query(Song, mix_songs.c.track_number)\
                          .join(mix_songs)\
                          .filter(mix_songs.c.mix_id == self.id)\
                          .order_by(mix_songs.c.track_number.asc().nullslast(), Song.title)
        
        return [song for song, track_number in query.all()]
    
    def add_song(self, song, track_number=None):
        """Add a song to this mix with optional track number."""
        if song not in self.songs:
            self.songs.append(song)
            # If track number is provided, we need to update the association table
            if track_number is not None:
                # This would require a direct SQL update to set track_number
                # For now, we'll handle this in the logic layer
                pass
    
    def remove_song(self, song):
        """Remove a song from this mix."""
        if song in self.songs:
            self.songs.remove(song)
    
    def increment_play_count(self):
        """Increment the play count for this mix."""
        self.play_count += 1
        self.updated_at = datetime.utcnow()
    
    def increment_like_count(self):
        """Increment the like count for this mix."""
        self.like_count += 1
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert mix to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'genre': self.genre,
            'cover_image': self.cover_image,
            'visibility': self.visibility,
            'play_count': self.play_count,
            'like_count': self.like_count,
            'song_count': self.song_count,
            'total_duration': self.total_duration,
            'created_by_id': self.created_by_id,
            'created_by_name': self.created_by.full_name if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict_with_songs(self):
        """Convert mix to dictionary including songs."""
        result = self.to_dict()
        result['songs'] = [song.to_dict() for song in self.get_songs_ordered()]
        return result


class Song(db.Model):
    """Song model for individual music tracks."""
    
    __tablename__ = 'songs'
    
    # Primary key and timestamps
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Song information
    title = db.Column(db.String(200), nullable=False, index=True)
    artist = db.Column(db.String(200), index=True)
    genre = db.Column(db.String(50), index=True)
    
    # File information
    file_path = db.Column(db.String(500), nullable=False)  # Path to audio file
    file_name = db.Column(db.String(255), nullable=False)  # Original filename
    file_size = db.Column(db.Integer)  # File size in bytes
    file_format = db.Column(db.String(10))  # mp3, wav, etc.
    
    # Audio metadata
    duration_seconds = db.Column(db.Integer)  # Duration in seconds
    bitrate = db.Column(db.Integer)  # Audio bitrate
    sample_rate = db.Column(db.Integer)  # Sample rate
    
    # Content flags
    explicit = db.Column(db.Boolean, default=False, nullable=False)
    
    # Statistics
    play_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Relationships
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_by = db.relationship('User', backref=db.backref('songs', lazy=True))
    
    def __repr__(self):
        return f'<Song {self.title}>'
    
    @property
    def duration(self):
        """Get formatted duration string."""
        if not self.duration_seconds:
            return "0:00"
        
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    @property
    def file_size_mb(self):
        """Get file size in MB."""
        if not self.file_size:
            return 0
        return round(self.file_size / (1024 * 1024), 2)
    
    def get_mix_track_number(self, mix_id):
        """Get the track number for this song in a specific mix."""
        result = db.session.query(mix_songs.c.track_number)\
                          .filter(mix_songs.c.mix_id == mix_id)\
                          .filter(mix_songs.c.song_id == self.id)\
                          .first()
        return result[0] if result else None
    
    def increment_play_count(self):
        """Increment the play count for this song."""
        self.play_count += 1
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert song to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'genre': self.genre,
            'file_name': self.file_name,
            'file_format': self.file_format,
            'file_size_mb': self.file_size_mb,
            'duration': self.duration,
            'duration_seconds': self.duration_seconds,
            'bitrate': self.bitrate,
            'sample_rate': self.sample_rate,
            'explicit': self.explicit,
            'play_count': self.play_count,
            'uploaded_by_id': self.uploaded_by_id,
            'uploaded_by_name': self.uploaded_by.full_name if self.uploaded_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict_with_mixes(self):
        """Convert song to dictionary including mixes."""
        result = self.to_dict()
        result['mixes'] = [mix.to_dict() for mix in self.mixes]
        return result


class MixLike(db.Model):
    """Track which users like which mixes."""
    
    __tablename__ = 'mix_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    mix_id = db.Column(db.Integer, db.ForeignKey('mixes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    mix = db.relationship('Mix', backref=db.backref('likes', lazy=True))
    user = db.relationship('User', backref=db.backref('liked_mixes', lazy=True))
    
    # Ensure a user can only like a mix once
    __table_args__ = (db.UniqueConstraint('mix_id', 'user_id', name='unique_mix_like'),)
    
    def __repr__(self):
        return f'<MixLike mix_id={self.mix_id} user_id={self.user_id}>'


class PlayHistory(db.Model):
    """Track play history for songs and mixes."""
    
    __tablename__ = 'play_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=True)
    mix_id = db.Column(db.Integer, db.ForeignKey('mixes.id'), nullable=True)
    played_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    play_duration = db.Column(db.Integer)  # How long the user listened in seconds
    
    # Relationships
    user = db.relationship('User', backref=db.backref('play_history', lazy=True))
    song = db.relationship('Song', backref=db.backref('play_history', lazy=True))
    mix = db.relationship('Mix', backref=db.backref('play_history', lazy=True))
    
    def __repr__(self):
        if self.song_id:
            return f'<PlayHistory user_id={self.user_id} song_id={self.song_id}>'
        else:
            return f'<PlayHistory user_id={self.user_id} mix_id={self.mix_id}>'
    
    def to_dict(self):
        """Convert play history to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'song_id': self.song_id,
            'mix_id': self.mix_id,
            'played_at': self.played_at.isoformat() if self.played_at else None,
            'play_duration': self.play_duration,
            'song_title': self.song.title if self.song else None,
            'mix_title': self.mix.title if self.mix else None
        }
