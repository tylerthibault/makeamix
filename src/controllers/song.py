import datetime
from flask import Blueprint, abort, render_template, request, redirect, url_for, session, send_file
from src.models.song import Song
from src.services.user_service import UserService
from src.services.file_service import FileService

song_bp = Blueprint('songs', __name__, url_prefix='/songs')

# CREATE
@song_bp.route('/create', methods=['POST'])
def create_song():
    sond_data = {
        'title': request.form.get('title'),
        'content': request.files.get('song_file'),
        'user_id': UserService.get_current_user(hash_key=session.get('user_token')).id
    }
    print(sond_data)
    song = Song.create(sond_data)
    return redirect(url_for('user.home'))

# READ
@song_bp.route('/<int:song_id>')
def view_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        return "Song not found", 404
    
    current_user = UserService.get_current_user(session.get('user_token'))
    if not current_user or song.user_id != current_user.id:
        if not song.is_public:
            abort(404)
        return render_template('public/songs/view/index.html', song=song)
    return render_template('private/songs/view/index.html', song=song)

# UPDATE
@song_bp.route('/edit/<int:song_id>', methods=['GET', 'POST'])
def update_song(song_id):
    # need to make sure they own the song
    from src.models.song import Song
    song = Song.get_by_id(song_id)
    current_user = UserService.get_current_user(session.get('user_token'))
    if song.user_id != current_user.id:
        return "Unauthorized", 403
    
    if request.method == 'POST':
        song.update(song_id, {
            'title': request.form.get('title'),
            'is_public': bool(request.form.get('is_public')),
            'lyrics': request.form.get('lyrics')
        })
            

    return redirect(url_for('songs.view_song', song_id=song_id))

# DELETE
@song_bp.route('/delete/<int:song_id>', methods=['POST'])
def delete_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        return "Song not found", 404
    Song.delete(song_id)
    return redirect(url_for('user.home'))

# SERVE AUDIO FILE
@song_bp.route('/audio/<int:song_id>')
def serve_audio(song_id):
    song = Song.query.get(song_id)
    if not song:
        abort(404)
    
    # Check permissions - public songs or owner can access
    current_user = UserService.get_current_user(session.get('user_token'))
    if not song.is_public:
        if not current_user or song.user_id != current_user.id:
            abort(403)
    
    # Get file from storage (MinIO or local)
    file_data = FileService.get_file_path(song.file_path)
    if not file_data:
        abort(404)
    
    # For MinIO, file_data is BytesIO; for local, it's a Path
    if FileService.STORAGE_MODE == 'minio':
        # Stream from BytesIO object
        file_data.seek(0)
        return send_file(file_data, mimetype='audio/mpeg', download_name=f'{song.title}.mp3')
    else:
        # Serve from local filesystem
        if not file_data.exists():
            abort(404)
        return send_file(file_data, mimetype='audio/mpeg')