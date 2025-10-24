"""
Music controller for handling mix and song CRUD operations.
Thin controller following fat logic pattern.
"""
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash, current_app
from werkzeug.utils import secure_filename
import os
from src.logic.mix_logic import MixLogic, SongLogic
from src.models.user_model import User
from functools import wraps

# Create blueprint
music_bp = Blueprint('music', __name__, url_prefix='/music')


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    """Decorator to require teacher role for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('user.login'))
        
        user = User.query.get(session['user_id'])
        if not user or (user.user_type != 'teacher' and not user.has_role('teacher')):
            flash('Teacher access required.', 'error')
            return redirect(url_for('user.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


# Mix Routes
@music_bp.route('/mixes', methods=['GET'])
@login_required
def list_mixes():
    """List user's mixes."""
    try:
        user_id = session['user_id']
        mixes = MixLogic.get_user_mixes(user_id)
        
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'mixes': [mix.to_dict() for mix in mixes]
            })
        
        return render_template('private/teacher/my_mixes/index.html', mixes=mixes)
        
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'error': str(e)}), 500
        
        flash(f'Error loading mixes: {str(e)}', 'error')
        return redirect(url_for('user.dashboard'))


@music_bp.route('/mixes/create', methods=['GET', 'POST'])
@login_required
def create_mix():
    """Create a new mix."""
    if request.method == 'GET':
        user_id = session['user_id']
        user_mixes = MixLogic.get_user_mixes(user_id)
        return render_template('private/teacher/create_mix/index.html', user_mixes=user_mixes)
    
    try:
        user_id = session['user_id']
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Map form field names to expected names
        if not request.is_json:
            mapped_data = {
                'title': data.get('mix_title'),
                'description': data.get('mix_description'),
                'genre': data.get('mix_genre'),
                'visibility': data.get('mix_visibility')
            }
        else:
            mapped_data = data
        
        mix = MixLogic.create_mix(mapped_data, user_id)
        
        flash('Mix created successfully!', 'success')
        return redirect(url_for('music.list_mixes'))
        
    except ValueError as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(str(e), 'error')
        user_mixes = MixLogic.get_user_mixes(user_id)
        return render_template('private/teacher/create_mix/index.html', user_mixes=user_mixes)
    
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        
        flash('An error occurred while creating the mix.', 'error')
        user_mixes = MixLogic.get_user_mixes(user_id)
        return render_template('private/teacher/create_mix/index.html', user_mixes=user_mixes)


@music_bp.route('/mixes/<int:mix_id>', methods=['GET'])
@login_required
def get_mix(mix_id):
    """Get a specific mix."""
    try:
        mix = MixLogic.get_mix_by_id(mix_id)
        if not mix:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Mix not found'}), 404
            flash('Mix not found.', 'error')
            return redirect(url_for('music.list_mixes'))
        
        # Check visibility permissions
        user_id = session['user_id']
        if mix.visibility == 'private' and mix.created_by_id != user_id:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Access denied'}), 403
            flash('You do not have permission to view this mix.', 'error')
            return redirect(url_for('music.list_mixes'))
        
        if request.is_json:
            return jsonify({
                'success': True,
                'mix': mix.to_dict()
            })
        
        return render_template('private/teacher/mix_detail/index.html', mix=mix)
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        
        flash(f'Error loading mix: {str(e)}', 'error')
        return redirect(url_for('music.list_mixes'))


@music_bp.route('/mixes/<int:mix_id>', methods=['PUT'])
@login_required
def update_mix(mix_id):
    """Update a mix."""
    try:
        user_id = session['user_id']
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        mix = MixLogic.update_mix(mix_id, data, user_id)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Mix updated successfully',
                'mix': mix.to_dict()
            })
        
        flash('Mix updated successfully!', 'success')
        return redirect(url_for('music.get_mix', mix_id=mix_id))
        
    except ValueError as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(str(e), 'error')
        return redirect(url_for('music.get_mix', mix_id=mix_id))
    
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        
        flash('An error occurred while updating the mix.', 'error')
        return redirect(url_for('music.get_mix', mix_id=mix_id))


@music_bp.route('/mixes/<int:mix_id>', methods=['DELETE'])
@login_required
def delete_mix(mix_id):
    """Delete a mix."""
    try:
        user_id = session['user_id']
        MixLogic.delete_mix(mix_id, user_id)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Mix deleted successfully'
            })
        
        flash('Mix deleted successfully!', 'success')
        return redirect(url_for('music.list_mixes'))
        
    except ValueError as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(str(e), 'error')
        return redirect(url_for('music.list_mixes'))
    
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        
        flash('An error occurred while deleting the mix.', 'error')
        return redirect(url_for('music.list_mixes'))


@music_bp.route('/mixes/<int:mix_id>/songs', methods=['POST'])
@login_required
def add_song_to_mix(mix_id):
    """Add a song to a mix."""
    try:
        user_id = session['user_id']
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        song_id = data.get('song_id')
        track_number = data.get('track_number')
        
        if not song_id:
            raise ValueError('Song ID is required')
        
        MixLogic.add_song_to_mix(mix_id, int(song_id), track_number, user_id)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Song added to mix successfully'
            })
        
        flash('Song added to mix successfully!', 'success')
        return redirect(url_for('music.get_mix', mix_id=mix_id))
        
    except ValueError as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(str(e), 'error')
        return redirect(url_for('music.get_mix', mix_id=mix_id))
    
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        
        flash('An error occurred while adding the song to the mix.', 'error')
        return redirect(url_for('music.get_mix', mix_id=mix_id))


@music_bp.route('/mixes/<int:mix_id>/songs/<int:song_id>', methods=['DELETE'])
@login_required
def remove_song_from_mix(mix_id, song_id):
    """Remove a song from a mix."""
    try:
        user_id = session['user_id']
        MixLogic.remove_song_from_mix(mix_id, song_id, user_id)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Song removed from mix successfully'
            })
        
        flash('Song removed from mix successfully!', 'success')
        return redirect(url_for('music.get_mix', mix_id=mix_id))
        
    except ValueError as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(str(e), 'error')
        return redirect(url_for('music.get_mix', mix_id=mix_id))
    
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        
        flash('An error occurred while removing the song from the mix.', 'error')
        return redirect(url_for('music.get_mix', mix_id=mix_id))


@music_bp.route('/mixes/<int:mix_id>/like', methods=['POST'])
@login_required
def like_mix(mix_id):
    """Like a mix."""
    try:
        user_id = session['user_id']
        MixLogic.like_mix(mix_id, user_id)
        
        return jsonify({
            'success': True,
            'message': 'Mix liked successfully'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@music_bp.route('/mixes/<int:mix_id>/unlike', methods=['POST'])
@login_required
def unlike_mix(mix_id):
    """Unlike a mix."""
    try:
        user_id = session['user_id']
        MixLogic.unlike_mix(mix_id, user_id)
        
        return jsonify({
            'success': True,
            'message': 'Mix unliked successfully'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@music_bp.route('/mixes/<int:mix_id>/play', methods=['POST'])
@login_required
def record_mix_play(mix_id):
    """Record a mix play."""
    try:
        user_id = session['user_id']
        data = request.get_json() if request.is_json else request.form.to_dict()
        play_duration = data.get('play_duration')
        
        MixLogic.record_play(mix_id, user_id, play_duration)
        
        return jsonify({
            'success': True,
            'message': 'Play recorded successfully'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


# Song Routes
@music_bp.route('/songs', methods=['GET'])
@login_required
def list_songs():
    """List user's songs."""
    try:
        user_id = session['user_id']
        songs = SongLogic.get_user_songs(user_id)
        
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'songs': [song.to_dict() for song in songs]
            })
        
        return render_template('private/teacher/my_songs/index.html', songs=songs)
        
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'error': str(e)}), 500
        
        flash(f'Error loading songs: {str(e)}', 'error')
        return redirect(url_for('user.dashboard'))


@music_bp.route('/songs/upload', methods=['POST'])
@login_required
def upload_song():
    """Upload a new song."""
    try:
        user_id = session['user_id']
        
        # Check if file was uploaded
        if 'song_file' not in request.files:
            raise ValueError('No file uploaded')
        
        file = request.files['song_file']
        data = request.form.to_dict()
        
        # Get upload folder from app config
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/songs')
        
        # Create upload folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
        
        song = SongLogic.upload_song(file, data, user_id, upload_folder)
        
        # If mix_id is provided, add song to mix
        mix_id = data.get('mix_id')
        if mix_id:
            track_number = data.get('track_number')
            MixLogic.add_song_to_mix(int(mix_id), song.id, track_number, user_id)
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'message': 'Song uploaded successfully',
                'song': song.to_dict()
            })
        
        flash('Song uploaded successfully!', 'success')
        return redirect(url_for('music.create_mix'))
        
    except ValueError as e:
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(str(e), 'error')
        return redirect(url_for('music.create_mix'))
    
    except Exception as e:
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        
        flash('An error occurred while uploading the song.', 'error')
        return redirect(url_for('music.create_mix'))


@music_bp.route('/songs/<int:song_id>', methods=['GET'])
@login_required
def get_song(song_id):
    """Get a specific song."""
    try:
        song = SongLogic.get_song_by_id(song_id)
        if not song:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Song not found'}), 404
            flash('Song not found.', 'error')
            return redirect(url_for('music.list_songs'))
        
        if request.is_json:
            return jsonify({
                'success': True,
                'song': song.to_dict()
            })
        
        return render_template('private/teacher/song_detail/index.html', song=song)
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        
        flash(f'Error loading song: {str(e)}', 'error')
        return redirect(url_for('music.list_songs'))


@music_bp.route('/songs/<int:song_id>', methods=['PUT'])
@login_required
def update_song(song_id):
    """Update a song."""
    try:
        user_id = session['user_id']
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        song = SongLogic.update_song(song_id, data, user_id)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Song updated successfully',
                'song': song.to_dict()
            })
        
        flash('Song updated successfully!', 'success')
        return redirect(url_for('music.get_song', song_id=song_id))
        
    except ValueError as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(str(e), 'error')
        return redirect(url_for('music.get_song', song_id=song_id))
    
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        
        flash('An error occurred while updating the song.', 'error')
        return redirect(url_for('music.get_song', song_id=song_id))


@music_bp.route('/songs/<int:song_id>', methods=['DELETE'])
@login_required
def delete_song(song_id):
    """Delete a song."""
    try:
        user_id = session['user_id']
        SongLogic.delete_song(song_id, user_id)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Song deleted successfully'
            })
        
        flash('Song deleted successfully!', 'success')
        return redirect(url_for('music.list_songs'))
        
    except ValueError as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(str(e), 'error')
        return redirect(url_for('music.list_songs'))
    
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        
        flash('An error occurred while deleting the song.', 'error')
        return redirect(url_for('music.list_songs'))


@music_bp.route('/songs/<int:song_id>/play', methods=['POST'])
@login_required
def record_song_play(song_id):
    """Record a song play."""
    try:
        user_id = session['user_id']
        data = request.get_json() if request.is_json else request.form.to_dict()
        play_duration = data.get('play_duration')
        
        SongLogic.record_play(song_id, user_id, play_duration)
        
        return jsonify({
            'success': True,
            'message': 'Play recorded successfully'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


# Public Discovery Routes
@music_bp.route('/discover', methods=['GET'])
def discover_mixes():
    """Discover public mixes."""
    try:
        limit = request.args.get('limit', 20, type=int)
        mixes = MixLogic.get_public_mixes(limit)
        
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'mixes': [mix.to_dict() for mix in mixes]
            })
        
        return render_template('public/discover/index.html', mixes=mixes)
        
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'error': str(e)}), 500
        
        flash(f'Error loading public mixes: {str(e)}', 'error')
        return redirect(url_for('user.landing'))


# Error handlers
@music_bp.errorhandler(413)
def file_too_large(e):
    """Handle file too large error."""
    if request.is_json:
        return jsonify({'success': False, 'error': 'File too large'}), 413
    
    flash('File is too large. Please choose a smaller file.', 'error')
    return redirect(url_for('music.create_mix'))


@music_bp.errorhandler(400)
def bad_request(e):
    """Handle bad request error."""
    if request.is_json:
        return jsonify({'success': False, 'error': 'Bad request'}), 400
    
    flash('Invalid request.', 'error')
    return redirect(url_for('user.dashboard'))


@music_bp.errorhandler(404)
def not_found(e):
    """Handle not found error."""
    if request.is_json:
        return jsonify({'success': False, 'error': 'Resource not found'}), 404
    
    flash('The requested resource was not found.', 'error')
    return redirect(url_for('user.dashboard'))


@music_bp.errorhandler(500)
def internal_error(e):
    """Handle internal server error."""
    if request.is_json:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    flash('An internal error occurred. Please try again later.', 'error')
    return redirect(url_for('user.dashboard'))
