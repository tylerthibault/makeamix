import os
from pathlib import Path
from werkzeug.utils import secure_filename

class FileService:
    # Base upload directory
    UPLOAD_DIR = Path('uploads/songs')
    
    @staticmethod
    def _ensure_directory_exists(directory: Path):
        """Create directory if it doesn't exist"""
        directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_upload_path():
        """Get the absolute path to the upload directory"""
        base_path = Path(__file__).parent.parent.parent / FileService.UPLOAD_DIR
        FileService._ensure_directory_exists(base_path)
        return base_path
    
    @staticmethod
    def save_song_file(file_obj, user_id: int, short_id: str):
        """
        Save uploaded song file to filesystem.
        
        :param file_obj: File-like object from Flask's request.files
        :param user_id: ID of the user uploading the file
        :param short_id: Unique short identifier for the song
        :return: Relative file path or None if no file provided
        """
        if file_obj is None or file_obj.filename == '':
            return None
        
        # Get file extension
        original_filename = secure_filename(file_obj.filename)
        _, ext = os.path.splitext(original_filename)
        if not ext:
            ext = '.mp3'  # Default to mp3 if no extension
        
        # Create user directory
        user_dir = FileService.get_upload_path() / f'user_{user_id}'
        FileService._ensure_directory_exists(user_dir)
        
        # Create filename: song_{short_id}.ext
        filename = f'song_{short_id}{ext}'
        file_path = user_dir / filename
        
        # Save the file
        file_obj.save(str(file_path))
        
        # Return relative path for database storage
        relative_path = f'uploads/songs/user_{user_id}/{filename}'
        return relative_path
    
    @staticmethod
    def delete_song_file(file_path: str):
        """
        Delete a song file from the filesystem.
        
        :param file_path: Relative path to the file
        :return: True if deleted, False otherwise
        """
        if not file_path:
            return False
        
        try:
            full_path = Path(__file__).parent.parent.parent / file_path
            if full_path.exists():
                full_path.unlink()
                return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
        return False
    
    @staticmethod
    def get_file_path(relative_path: str):
        """
        Get absolute path from relative path.
        
        :param relative_path: Relative path stored in database
        :return: Absolute Path object
        """
        if not relative_path:
            return None
        return Path(__file__).parent.parent.parent / relative_path