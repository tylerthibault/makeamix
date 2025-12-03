from flask import Blueprint, abort, render_template, request, redirect, url_for, session, jsonify
from src.models.playlist import Playlist
from src.models.song import Song
from src.services.user_service import UserService

playlist_bp = Blueprint('playlists', __name__, url_prefix='/playlists')


# CREATE
@playlist_bp.route('/create', methods=['GET', 'POST'])
def create_playlist():
    current_user = UserService.get_current_user(session.get('user_token'))
    if not current_user:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        playlist_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description', ''),
            'is_public': bool(request.form.get('is_public')),
            'user_id': current_user.id
        }
        playlist = Playlist.create(playlist_data)
        return redirect(url_for('playlists.view_playlist', playlist_id=playlist.id))
    
    return render_template('private/playlists/forms/create.html', current_user=current_user)


# READ - View all user playlists
@playlist_bp.route('/')
def list_playlists():
    current_user = UserService.get_current_user(session.get('user_token'))
    if not current_user:
        return redirect(url_for('auth.login'))
    
    playlists = Playlist.get_by_user(current_user.id)
    return render_template('private/playlists/index.html', 
                         playlists=playlists, 
                         current_user=current_user)


# READ - View single playlist
@playlist_bp.route('/<int:playlist_id>')
def view_playlist(playlist_id):
    playlist = Playlist.get_by_id(playlist_id)
    if not playlist:
        abort(404)
    
    current_user = UserService.get_current_user(session.get('user_token'))
    
    # Check permissions
    if not playlist.is_public and (not current_user or playlist.user_id != current_user.id):
        abort(404)
    
    # Get songs in order
    songs = playlist.get_ordered_songs()
    
    # Determine which template to use
    if current_user and playlist.user_id == current_user.id:
        return render_template('private/playlists/view/index.html', 
                             playlist=playlist, 
                             songs=songs,
                             current_user=current_user)
    else:
        return render_template('public/playlists/view/index.html', 
                             playlist=playlist, 
                             songs=songs)


# UPDATE
@playlist_bp.route('/edit/<int:playlist_id>', methods=['POST'])
def update_playlist(playlist_id):
    current_user = UserService.get_current_user(session.get('user_token'))
    if not current_user:
        return redirect(url_for('auth.login'))
    
    playlist = Playlist.get_by_id(playlist_id)
    if not playlist or playlist.user_id != current_user.id:
        abort(403)
    
    playlist.update(playlist_id, {
        'name': request.form.get('name'),
        'description': request.form.get('description'),
        'is_public': bool(request.form.get('is_public'))
    })
    
    return redirect(url_for('playlists.view_playlist', playlist_id=playlist_id))


# DELETE
@playlist_bp.route('/delete/<int:playlist_id>', methods=['POST'])
def delete_playlist(playlist_id):
    current_user = UserService.get_current_user(session.get('user_token'))
    if not current_user:
        return redirect(url_for('auth.login'))
    
    playlist = Playlist.get_by_id(playlist_id)
    if not playlist or playlist.user_id != current_user.id:
        abort(403)
    
    Playlist.delete(playlist_id)
    return redirect(url_for('playlists.list_playlists'))


# Add song to playlist
@playlist_bp.route('/<int:playlist_id>/add_song/<int:song_id>', methods=['POST'])
def add_song_to_playlist(playlist_id, song_id):
    current_user = UserService.get_current_user(session.get('user_token'))
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    playlist = Playlist.get_by_id(playlist_id)
    if not playlist or playlist.user_id != current_user.id:
        return jsonify({'error': 'Forbidden'}), 403
    
    song = Song.get_by_id(song_id)
    if not song:
        return jsonify({'error': 'Song not found'}), 404
    
    success = playlist.add_song(song_id)
    if success:
        return jsonify({'success': True, 'message': 'Song added to playlist'})
    else:
        return jsonify({'error': 'Song already in playlist'}), 400


# Remove song from playlist
@playlist_bp.route('/<int:playlist_id>/remove_song/<int:song_id>', methods=['POST'])
def remove_song_from_playlist(playlist_id, song_id):
    current_user = UserService.get_current_user(session.get('user_token'))
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    playlist = Playlist.get_by_id(playlist_id)
    if not playlist or playlist.user_id != current_user.id:
        return jsonify({'error': 'Forbidden'}), 403
    
    success = playlist.remove_song(song_id)
    if success:
        return jsonify({'success': True, 'message': 'Song removed from playlist'})
    else:
        return jsonify({'error': 'Song not in playlist'}), 400


# Reorder songs in playlist
@playlist_bp.route('/<int:playlist_id>/reorder', methods=['POST'])
def reorder_playlist(playlist_id):
    current_user = UserService.get_current_user(session.get('user_token'))
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    playlist = Playlist.get_by_id(playlist_id)
    if not playlist or playlist.user_id != current_user.id:
        return jsonify({'error': 'Forbidden'}), 403
    
    song_ids = request.json.get('song_ids', [])
    playlist.reorder_songs(song_ids)
    
    return jsonify({'success': True, 'message': 'Playlist reordered'})
