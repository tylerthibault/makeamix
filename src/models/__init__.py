"""
Models package for the Make a Mix application.
This module imports and exposes all the models for easy access.
"""

# Import user models
from .user_model import User, Teacher, Student, Role, user_roles

# Import mix and song models
from .mix_model import Mix, Song, mix_songs, MixLike, PlayHistory

# Import roles model if it exists separately
try:
    from .roles_model import *
except ImportError:
    pass

# Make all models available when importing from models package
__all__ = [
    'User', 'Teacher', 'Student', 'Role', 'user_roles',
    'Album', 'Song', 'album_songs', 'AlbumLike', 'PlayHistory'
]