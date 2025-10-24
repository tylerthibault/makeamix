"""
Mix and Song business logic layer.
Contains all business rules and operations for mix and song management.
"""
import os
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename
from src import db
from src.models.mix_model import Mix, Song, MixLike, PlayHistory, mix_songs


class MixLogic:
    """Business logic for mix operations."""
    
    @staticmethod
    def create_mix(data, user_id):
        """Create a new mix with validation and business rules."""
        # Basic validation
        if not data.get('title'):
            raise ValueError('Mix title is required')
        
        if len(data['title'].strip()) < 3:
            raise ValueError('Mix title must be at least 3 characters long')
        
        # Validate visibility
        valid_visibilities = ['private', 'class', 'public']
        visibility = data.get('visibility', 'private')
        if visibility not in valid_visibilities:
            raise ValueError(f'Visibility must be one of: {", ".join(valid_visibilities)}')
        
        try:
            # Use the model's factory method to create the mix
            mix = Mix.create_new_mix(
                title=data['title'].strip(),
                description=data.get('description', '').strip() or None,
                genre=data.get('genre', '').strip() or None,
                visibility=visibility,
                created_by_id=user_id
            )
            
            return mix
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Failed to create mix: {str(e)}')
    
    @staticmethod
    def get_mix_by_id(mix_id):
        """Get mix by ID."""
        return Mix.query.get(mix_id)
    
    @staticmethod
    def get_user_mixes(user_id, visibility=None):
        """Get all mixes created by a user."""
        query = Mix.query.filter_by(created_by_id=user_id)
        
        if visibility:
            query = query.filter_by(visibility=visibility)
        
        return query.order_by(Mix.updated_at.desc()).all()
    
    @staticmethod
    def get_public_mixes(limit=None):
        """Get public mixes for discovery."""
        query = Mix.query.filter_by(visibility='public').order_by(Mix.play_count.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def update_mix(mix_id, data, user_id):
        """Update an existing mix with validation."""
        mix = MixLogic.get_mix_by_id(mix_id)
        if not mix:
            raise ValueError('Mix not found')
        
        # Check ownership
        if mix.created_by_id != user_id:
            raise ValueError('You can only edit your own mixes')
        
        # Validate title if provided
        if 'title' in data:
            if not data['title'] or len(data['title'].strip()) < 3:
                raise ValueError('Mix title must be at least 3 characters long')
            mix.title = data['title'].strip()
        
        # Validate visibility if provided
        if 'visibility' in data:
            valid_visibilities = ['private', 'class', 'public']
            if data['visibility'] not in valid_visibilities:
                raise ValueError(f'Visibility must be one of: {", ".join(valid_visibilities)}')
            mix.visibility = data['visibility']
        
        # Update other fields
        if 'description' in data:
            mix.description = data['description'].strip() or None
        
        if 'genre' in data:
            mix.genre = data['genre'].strip() or None
        
        mix.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return mix
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Failed to update mix: {str(e)}')
    
    @staticmethod
    def delete_mix(mix_id, user_id):
        """Delete a mix and handle related data."""
        mix = MixLogic.get_mix_by_id(mix_id)
        if not mix:
            raise ValueError('Mix not found')
        
        # Check ownership
        if mix.created_by_id != user_id:
            raise ValueError('You can only delete your own mixes')
        
        try:
            # Remove mix-song associations
            db.session.execute(mix_songs.delete().where(mix_songs.c.mix_id == mix_id))
            
            # Delete related likes and play history
            MixLike.query.filter_by(mix_id=mix_id).delete()
            PlayHistory.query.filter_by(mix_id=mix_id).delete()
            
            # Delete cover image file if exists
            if mix.cover_image:
                MixLogic._delete_cover_image(mix.cover_image)
            
            # Delete mix
            db.session.delete(mix)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Failed to delete mix: {str(e)}')
    
    @staticmethod
    def add_song_to_mix(mix_id, song_id, track_number=None, user_id=None):
        """Add a song to a mix with optional track number."""
        mix = MixLogic.get_mix_by_id(mix_id)
        song = SongLogic.get_song_by_id(song_id)
        
        if not mix:
            raise ValueError('Mix not found')
        
        if not song:
            raise ValueError('Song not found')
        
        # Check ownership if user_id provided
        if user_id and mix.created_by_id != user_id:
            raise ValueError('You can only modify your own mixes')
        
        # Check if song is already in mix
        if song in mix.songs:
            raise ValueError('Song is already in this mix')
        
        try:
            # Add song to mix
            mix.songs.append(song)
            
            # Set track number if provided
            if track_number is not None:
                # Update the association table with track number
                db.session.execute(
                    mix_songs.update()
                    .where(mix_songs.c.mix_id == mix_id)
                    .where(mix_songs.c.song_id == song_id)
                    .values(track_number=track_number)
                )
            
            mix.updated_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Failed to add song to mix: {str(e)}')
    
    @staticmethod
    def remove_song_from_mix(mix_id, song_id, user_id=None):
        """Remove a song from a mix."""
        mix = MixLogic.get_mix_by_id(mix_id)
        song = SongLogic.get_song_by_id(song_id)
        
        if not mix:
            raise ValueError('Mix not found')
        
        if not song:
            raise ValueError('Song not found')
        
        # Check ownership if user_id provided
        if user_id and mix.created_by_id != user_id:
            raise ValueError('You can only modify your own mixes')
        
        if song not in mix.songs:
            raise ValueError('Song is not in this mix')
        
        try:
            mix.songs.remove(song)
            mix.updated_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Failed to remove song from mix: {str(e)}')
    
    @staticmethod
    def like_mix(mix_id, user_id):
        """Add a like to a mix."""
        mix = MixLogic.get_mix_by_id(mix_id)
        if not mix:
            raise ValueError('Mix not found')
        
        # Check if already liked
        existing_like = MixLike.query.filter_by(mix_id=mix_id, user_id=user_id).first()
        if existing_like:
            raise ValueError('You have already liked this mix')
        
        try:
            like = MixLike(mix_id=mix_id, user_id=user_id)
            db.session.add(like)
            
            # Update mix like count
            mix.like_count += 1
            mix.updated_at = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Failed to like mix: {str(e)}')
    
    @staticmethod
    def unlike_mix(mix_id, user_id):
        """Remove a like from a mix."""
        mix = MixLogic.get_mix_by_id(mix_id)
        if not mix:
            raise ValueError('Mix not found')
        
        like = MixLike.query.filter_by(mix_id=mix_id, user_id=user_id).first()
        if not like:
            raise ValueError('You have not liked this mix')
        
        try:
            db.session.delete(like)
            
            # Update mix like count
            mix.like_count = max(0, mix.like_count - 1)
            mix.updated_at = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Failed to unlike mix: {str(e)}')
    
    @staticmethod
    def record_play(mix_id, user_id, play_duration=None):
        """Record a mix play in history."""
        mix = MixLogic.get_mix_by_id(mix_id)
        if not mix:
            raise ValueError('Mix not found')
        
        try:
            # Record play history
            play_record = PlayHistory(
                mix_id=mix_id,
                user_id=user_id,
                play_duration=play_duration
            )
            db.session.add(play_record)
            
            # Update mix play count
            mix.play_count += 1
            mix.updated_at = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Failed to record play: {str(e)}')
    
    @staticmethod
    def _delete_cover_image(cover_image_path):
        """Delete cover image file from filesystem."""
        try:
            # This would be implemented based on your file storage strategy
            # For now, just a placeholder
            pass
        except Exception:
            # Log error but don't fail the operation
            pass


class SongLogic:
    """Business logic for song operations."""
    
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @staticmethod
    def upload_song(file, data, user_id, upload_folder):
        """Upload and create a new song with validation."""
        # Validate file
        if not file or file.filename == '':
            raise ValueError('No file selected')
        
        if not SongLogic._allowed_file(file.filename):
            raise ValueError(f'File type not allowed. Allowed types: {", ".join(SongLogic.ALLOWED_EXTENSIONS)}')
        
        # Validate file size (this should be done by the web server, but double-check)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > SongLogic.MAX_FILE_SIZE:
            raise ValueError(f'File size too large. Maximum size: {SongLogic.MAX_FILE_SIZE // (1024*1024)}MB')
        
        # Basic validation
        title = data.get('title', '').strip()
        if not title:
            # Use filename as title if not provided
            title = os.path.splitext(file.filename)[0]
        
        if len(title) < 1:
            raise ValueError('Song title is required')
        
        try:
            # Generate unique filename
            filename = SongLogic._generate_unique_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            
            # Save file
            file.save(file_path)
            
            # Extract audio metadata (this would require a library like mutagen)
            # For now, we'll use placeholder values
            duration_seconds = SongLogic._extract_duration(file_path)
            
            # Create song record
            song = Song(
                title=title,
                artist=data.get('artist', '').strip() or None,
                genre=data.get('genre', '').strip() or None,
                file_path=file_path,
                file_name=file.filename,
                file_size=file_size,
                file_format=SongLogic._get_file_extension(file.filename),
                duration_seconds=duration_seconds,
                explicit=data.get('explicit', False),
                uploaded_by_id=user_id
            )
            
            db.session.add(song)
            db.session.commit()
            
            return song
            
        except Exception as e:
            # Clean up file if song creation failed
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            
            db.session.rollback()
            raise ValueError(f'Failed to upload song: {str(e)}')
    
    @staticmethod
    def get_song_by_id(song_id):
        """Get song by ID."""
        return Song.query.get(song_id)
    
    @staticmethod
    def get_user_songs(user_id):
        """Get all songs uploaded by a user."""
        return Song.query.filter_by(uploaded_by_id=user_id).order_by(Song.updated_at.desc()).all()
    
    @staticmethod
    def update_song(song_id, data, user_id):
        """Update song metadata."""
        song = SongLogic.get_song_by_id(song_id)
        if not song:
            raise ValueError('Song not found')
        
        # Check ownership
        if song.uploaded_by_id != user_id:
            raise ValueError('You can only edit your own songs')
        
        # Validate title if provided
        if 'title' in data:
            if not data['title'] or len(data['title'].strip()) < 1:
                raise ValueError('Song title is required')
            song.title = data['title'].strip()
        
        # Update other fields
        if 'artist' in data:
            song.artist = data['artist'].strip() or None
        
        if 'genre' in data:
            song.genre = data['genre'].strip() or None
        
        if 'explicit' in data:
            song.explicit = bool(data['explicit'])
        
        song.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return song
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Failed to update song: {str(e)}')
    
    @staticmethod
    def delete_song(song_id, user_id):
        """Delete a song and its file."""
        song = SongLogic.get_song_by_id(song_id)
        if not song:
            raise ValueError('Song not found')
        
        # Check ownership
        if song.uploaded_by_id != user_id:
            raise ValueError('You can only delete your own songs')
        
        try:
            # Remove song from all mixes
            db.session.execute(mix_songs.delete().where(mix_songs.c.song_id == song_id))
            
            # Delete play history
            PlayHistory.query.filter_by(song_id=song_id).delete()
            
            # Delete file
            if song.file_path and os.path.exists(song.file_path):
                os.remove(song.file_path)
            
            # Delete song record
            db.session.delete(song)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Failed to delete song: {str(e)}')
    
    @staticmethod
    def record_play(song_id, user_id, play_duration=None):
        """Record a song play in history."""
        song = SongLogic.get_song_by_id(song_id)
        if not song:
            raise ValueError('Song not found')
        
        try:
            # Record play history
            play_record = PlayHistory(
                song_id=song_id,
                user_id=user_id,
                play_duration=play_duration
            )
            db.session.add(play_record)
            
            # Update song play count
            song.play_count += 1
            song.updated_at = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Failed to record play: {str(e)}')
    
    @staticmethod
    def _allowed_file(filename):
        """Check if file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in SongLogic.ALLOWED_EXTENSIONS
    
    @staticmethod
    def _get_file_extension(filename):
        """Get file extension."""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    @staticmethod
    def _generate_unique_filename(filename):
        """Generate a unique filename to prevent conflicts."""
        name, ext = os.path.splitext(filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        hash_suffix = hashlib.md5(f"{name}{timestamp}".encode()).hexdigest()[:8]
        return f"{secure_filename(name)}_{timestamp}_{hash_suffix}{ext}"
    
    @staticmethod
    def _extract_duration(file_path):
        """Extract audio duration from file. Placeholder implementation."""
        # This would require a library like mutagen, librosa, or similar
        # For now, return None - this should be implemented based on your needs
        return None