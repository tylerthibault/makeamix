"""
This module contains imports and references to the Song model.
The actual Song model is defined in mix_model.py to keep
related models together due to their many-to-many relationship.
"""

# Import the models from mix_model for convenience
from .mix_model import Song, Mix, mix_songs, MixLike, PlayHistory

# Make the models available when importing from this module
__all__ = ['Song', 'Mix', 'mix_songs', 'MixLike', 'PlayHistory']
