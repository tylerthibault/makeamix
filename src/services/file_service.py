import os
from pathlib import Path
from werkzeug.utils import secure_filename
from minio import Minio
from minio.error import S3Error
from io import BytesIO

class FileService:
    # Base upload directory (for local fallback)
    UPLOAD_DIR = Path('uploads/songs')
    
    # MinIO configuration from environment variables
    MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT')
    MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
    MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
    MINIO_BUCKET = os.environ.get('MINIO_BUCKET', 'makeamix-songs')
    MINIO_SECURE = os.environ.get('MINIO_SECURE', 'true').lower() == 'true'
    
    # Storage mode: 'minio' or 'local'
    STORAGE_MODE = 'minio' if MINIO_ENDPOINT else 'local'
    
    _minio_client = None
    
    @staticmethod
    def _get_minio_client():
        """Get or create MinIO client"""
        if FileService._minio_client is None and FileService.STORAGE_MODE == 'minio':
            FileService._minio_client = Minio(
                FileService.MINIO_ENDPOINT,
                access_key=FileService.MINIO_ACCESS_KEY,
                secret_key=FileService.MINIO_SECRET_KEY,
                secure=FileService.MINIO_SECURE
            )
            # Ensure bucket exists
            try:
                if not FileService._minio_client.bucket_exists(FileService.MINIO_BUCKET):
                    FileService._minio_client.make_bucket(FileService.MINIO_BUCKET)
                    print(f"Created MinIO bucket: {FileService.MINIO_BUCKET}")
            except S3Error as e:
                print(f"Error creating MinIO bucket: {e}")
        return FileService._minio_client
    
    @staticmethod
    def _ensure_directory_exists(directory: Path):
        """Create directory if it doesn't exist (for local storage)"""
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
        Save uploaded song file to MinIO or local filesystem.
        
        :param file_obj: File-like object from Flask's request.files
        :param user_id: ID of the user uploading the file
        :param short_id: Unique short identifier for the song
        :return: Relative file path or object key
        """
        if file_obj is None or file_obj.filename == '':
            return None
        
        # Get file extension
        original_filename = secure_filename(file_obj.filename)
        _, ext = os.path.splitext(original_filename)
        if not ext:
            ext = '.mp3'  # Default to mp3 if no extension
        
        # Create object key: user_{user_id}/song_{short_id}.ext
        object_key = f'user_{user_id}/song_{short_id}{ext}'
        
        if FileService.STORAGE_MODE == 'minio':
            # Save to MinIO
            try:
                client = FileService._get_minio_client()
                
                # Read file data
                file_data = file_obj.read()
                file_size = len(file_data)
                file_obj.seek(0)  # Reset file pointer
                
                # Upload to MinIO
                client.put_object(
                    FileService.MINIO_BUCKET,
                    object_key,
                    BytesIO(file_data),
                    file_size,
                    content_type='audio/mpeg'
                )
                
                print(f"Uploaded to MinIO: {object_key}")
                return object_key
                
            except S3Error as e:
                print(f"Error uploading to MinIO: {e}")
                raise
        else:
            # Save to local filesystem (fallback)
            user_dir = FileService.get_upload_path() / f'user_{user_id}'
            FileService._ensure_directory_exists(user_dir)
            
            filename = f'song_{short_id}{ext}'
            file_path = user_dir / filename
            
            # Save the file
            file_obj.save(str(file_path))
            
            print(f"Saved locally: {file_path}")
            
            # Return relative path for database storage
            relative_path = f'uploads/songs/user_{user_id}/song_{short_id}{ext}'
            return relative_path
    
    @staticmethod
    def delete_song_file(file_path: str):
        """
        Delete a song file from MinIO or local filesystem.
        
        :param file_path: Relative path or object key
        :return: True if deleted, False otherwise
        """
        if not file_path:
            return False
        
        if FileService.STORAGE_MODE == 'minio':
            # Delete from MinIO
            try:
                client = FileService._get_minio_client()
                client.remove_object(FileService.MINIO_BUCKET, file_path)
                print(f"Deleted from MinIO: {file_path}")
                return True
            except S3Error as e:
                print(f"Error deleting from MinIO: {e}")
                return False
        else:
            # Delete from local filesystem
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
        Get file data from MinIO or absolute path from local filesystem.
        
        :param relative_path: Relative path or object key stored in database
        :return: For local: Absolute Path object, For MinIO: BytesIO object
        """
        if not relative_path:
            return None
        
        if FileService.STORAGE_MODE == 'minio':
            # Get from MinIO
            try:
                client = FileService._get_minio_client()
                response = client.get_object(FileService.MINIO_BUCKET, relative_path)
                return BytesIO(response.read())
            except S3Error as e:
                print(f"Error getting file from MinIO: {e}")
                return None
        else:
            # Get from local filesystem
            return Path(__file__).parent.parent.parent / relative_path