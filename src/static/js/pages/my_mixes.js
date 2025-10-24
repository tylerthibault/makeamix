/**
 * My Mixes Page JavaScript
 * Handles tab switching, view controls, search, and interactive features
 */

class MyMixesPage {
    constructor() {
        this.currentView = 'grid';
        this.currentTab = 'albums';
        this.init();
    }

    init() {
        this.bindTabEvents();
        this.bindViewControls();
        this.bindSearchFunctionality();
        this.bindPlayButtons();
        this.bindEditButtons();
        this.bindDeleteButtons();
        this.initializeTooltips();
    }

    bindTabEvents() {
        const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
        tabButtons.forEach(button => {
            button.addEventListener('shown.bs.tab', (e) => {
                this.currentTab = e.target.getAttribute('data-bs-target').includes('albums') ? 'albums' : 'songs';
                this.updateViewControls();
            });
        });
    }

    bindViewControls() {
        const gridViewBtn = document.getElementById('gridViewBtn');
        const listViewBtn = document.getElementById('listViewBtn');

        if (gridViewBtn && listViewBtn) {
            gridViewBtn.addEventListener('click', () => this.switchView('grid'));
            listViewBtn.addEventListener('click', () => this.switchView('list'));
        }
    }

    bindSearchFunctionality() {
        const searchInput = document.getElementById('songSearch');
        const searchBtn = document.getElementById('searchBtn');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.handleSearch(e.target.value);
                }
            });
        }

        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                if (searchInput) {
                    this.handleSearch(searchInput.value);
                }
            });
        }
    }

    bindPlayButtons() {
        // Album play buttons
        const playAlbumBtns = document.querySelectorAll('.play-album-btn');
        playAlbumBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const albumId = btn.getAttribute('data-album-id');
                this.playAlbum(albumId);
            });
        });

        // Song play buttons
        const playSongBtns = document.querySelectorAll('.play-song-btn');
        playSongBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const songId = btn.getAttribute('data-song-id');
                this.playSong(songId);
            });
        });
    }

    bindEditButtons() {
        // Edit album buttons
        const editAlbumBtns = document.querySelectorAll('[data-bs-target="#editAlbumModal"]');
        editAlbumBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const albumId = btn.getAttribute('data-album-id');
                this.loadEditAlbumForm(albumId);
            });
        });

        // Edit song buttons
        const editSongBtns = document.querySelectorAll('[data-bs-target="#editSongModal"]');
        editSongBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const songId = btn.getAttribute('data-song-id');
                this.loadEditSongForm(songId);
            });
        });
    }

    bindDeleteButtons() {
        // Delete album buttons
        const deleteAlbumBtns = document.querySelectorAll('.delete-album-btn');
        deleteAlbumBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const albumId = btn.getAttribute('data-album-id');
                const albumTitle = btn.getAttribute('data-album-title');
                this.confirmDeleteAlbum(albumId, albumTitle);
            });
        });

        // Delete song buttons
        const deleteSongBtns = document.querySelectorAll('.delete-song-btn');
        deleteSongBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const songId = btn.getAttribute('data-song-id');
                const songTitle = btn.getAttribute('data-song-title');
                this.confirmDeleteSong(songId, songTitle);
            });
        });
    }

    switchView(view) {
        this.currentView = view;
        
        const gridBtn = document.getElementById('gridViewBtn');
        const listBtn = document.getElementById('listViewBtn');
        const albumsContainer = document.getElementById('albumsContainer');

        if (gridBtn && listBtn && albumsContainer) {
            // Update button states
            gridBtn.classList.toggle('active', view === 'grid');
            listBtn.classList.toggle('active', view === 'list');

            // Update container class
            if (view === 'list') {
                albumsContainer.classList.add('albums-list-view');
                albumsContainer.classList.remove('albums-grid-view');
            } else {
                albumsContainer.classList.add('albums-grid-view');
                albumsContainer.classList.remove('albums-list-view');
            }
        }
    }

    updateViewControls() {
        const viewControls = document.querySelector('.view-controls');
        if (viewControls) {
            // Show view controls only for albums tab
            viewControls.style.display = this.currentTab === 'albums' ? 'block' : 'none';
        }
    }

    handleSearch(query) {
        const searchTerm = query.toLowerCase().trim();
        const songRows = document.querySelectorAll('.song-row');

        songRows.forEach(row => {
            const title = row.querySelector('.song-title')?.textContent.toLowerCase() || '';
            const artist = row.querySelector('td:nth-child(3)')?.textContent.toLowerCase() || '';
            const album = row.querySelector('.album-link')?.textContent.toLowerCase() || '';

            const matches = title.includes(searchTerm) || 
                          artist.includes(searchTerm) || 
                          album.includes(searchTerm);

            row.style.display = matches ? '' : 'none';
        });

        // Show/hide empty state if no results
        this.updateSearchResults(query, songRows);
    }

    updateSearchResults(query, songRows) {
        const visibleRows = Array.from(songRows).filter(row => row.style.display !== 'none');
        const songsContainer = document.querySelector('.songs-container');
        
        // Remove existing no-results message
        const existingMessage = songsContainer?.querySelector('.no-search-results');
        if (existingMessage) {
            existingMessage.remove();
        }

        // Show no results message if needed
        if (query.trim() && visibleRows.length === 0 && songsContainer) {
            const noResultsDiv = document.createElement('div');
            noResultsDiv.className = 'no-search-results empty-state';
            noResultsDiv.innerHTML = `
                <div class="empty-state__icon">
                    <i class="bi bi-search"></i>
                </div>
                <h3 class="empty-state__title">No songs found</h3>
                <p class="empty-state__message">
                    No songs match your search for "${query}". Try different keywords.
                </p>
            `;
            songsContainer.appendChild(noResultsDiv);
        }
    }

    playAlbum(albumId) {
        // Show loading state
        const playBtn = document.querySelector(`[data-album-id="${albumId}"].play-album-btn`);
        if (playBtn) {
            const originalIcon = playBtn.innerHTML;
            playBtn.innerHTML = '<i class="bi bi-spinner bi-spin"></i>';
            
            // Simulate API call
            setTimeout(() => {
                playBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
                this.showToast('Playing album...', 'info');
                
                // Reset after 2 seconds
                setTimeout(() => {
                    playBtn.innerHTML = originalIcon;
                }, 2000);
            }, 500);
        }
    }

    playSong(songId) {
        // Show loading state
        const playBtn = document.querySelector(`[data-song-id="${songId}"].play-song-btn`);
        if (playBtn) {
            const originalIcon = playBtn.innerHTML;
            playBtn.innerHTML = '<i class="bi bi-spinner bi-spin"></i>';
            
            // Simulate API call
            setTimeout(() => {
                playBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
                this.showToast('Playing song...', 'info');
                
                // Reset after 2 seconds
                setTimeout(() => {
                    playBtn.innerHTML = originalIcon;
                }, 2000);
            }, 500);
        }
    }

    loadEditAlbumForm(albumId) {
        // TODO: Load album data from API
        const modal = document.getElementById('editAlbumModal');
        const modalBody = modal?.querySelector('.modal-body');
        const albumIdInput = document.getElementById('editAlbumId');

        if (albumIdInput) {
            albumIdInput.value = albumId;
        }

        if (modalBody) {
            modalBody.innerHTML = `
                <div class="row g-3">
                    <div class="col-12">
                        <label for="editMixTitle" class="form-label">Album Title *</label>
                        <input type="text" class="form-control" id="editMixTitle" name="mix_title" required>
                    </div>
                    <div class="col-12">
                        <label for="editMixDescription" class="form-label">Description</label>
                        <textarea class="form-control" id="editMixDescription" name="mix_description" rows="3"></textarea>
                    </div>
                    <div class="col-md-6">
                        <label for="editMixGenre" class="form-label">Genre</label>
                        <select class="form-select" id="editMixGenre" name="mix_genre">
                            <option value="">Select a genre</option>
                            <option value="pop">Pop</option>
                            <option value="rock">Rock</option>
                            <option value="hip-hop">Hip-Hop</option>
                            <option value="electronic">Electronic</option>
                            <option value="classical">Classical</option>
                            <option value="jazz">Jazz</option>
                            <option value="country">Country</option>
                            <option value="r&b">R&B</option>
                            <option value="indie">Indie</option>
                            <option value="alternative">Alternative</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="col-md-6">
                        <label for="editMixVisibility" class="form-label">Visibility</label>
                        <select class="form-select" id="editMixVisibility" name="mix_visibility">
                            <option value="private">Private (Only me)</option>
                            <option value="class">Class Only</option>
                            <option value="public">Public</option>
                        </select>
                    </div>
                </div>
            `;
        }
    }

    loadEditSongForm(songId) {
        // TODO: Load song data from API
        const modal = document.getElementById('editSongModal');
        const modalBody = modal?.querySelector('.modal-body');
        const songIdInput = document.getElementById('editSongId');

        if (songIdInput) {
            songIdInput.value = songId;
        }

        if (modalBody) {
            modalBody.innerHTML = `
                <div class="row g-3">
                    <div class="col-12">
                        <label for="editSongTitle" class="form-label">Song Title *</label>
                        <input type="text" class="form-control" id="editSongTitle" name="song_title" required>
                    </div>
                    <div class="col-12">
                        <label for="editSongArtist" class="form-label">Artist</label>
                        <input type="text" class="form-control" id="editSongArtist" name="song_artist">
                    </div>
                    <div class="col-md-6">
                        <label for="editTrackNumber" class="form-label">Track Number</label>
                        <input type="number" class="form-control" id="editTrackNumber" name="track_number" min="1">
                    </div>
                    <div class="col-md-6">
                        <label for="editSongGenre" class="form-label">Genre</label>
                        <input type="text" class="form-control" id="editSongGenre" name="song_genre">
                    </div>
                </div>
            `;
        }
    }

    confirmDeleteAlbum(albumId, albumTitle) {
        if (confirm(`Are you sure you want to delete the album "${albumTitle}"? This action cannot be undone and will also delete all songs in this album.`)) {
            this.deleteAlbum(albumId);
        }
    }

    confirmDeleteSong(songId, songTitle) {
        if (confirm(`Are you sure you want to delete the song "${songTitle}"? This action cannot be undone.`)) {
            this.deleteSong(songId);
        }
    }

    deleteAlbum(albumId) {
        // TODO: Implement actual deletion via API
        this.showToast('Album deleted successfully', 'success');
        
        // Remove from UI
        const albumCard = document.querySelector(`[data-album-id="${albumId}"]`)?.closest('.album-card');
        if (albumCard) {
            albumCard.style.opacity = '0';
            albumCard.style.transform = 'scale(0.8)';
            setTimeout(() => {
                albumCard.remove();
                this.updateStatistics();
            }, 300);
        }
    }

    deleteSong(songId) {
        // TODO: Implement actual deletion via API
        this.showToast('Song deleted successfully', 'success');
        
        // Remove from UI
        const songRow = document.querySelector(`[data-song-id="${songId}"]`);
        if (songRow) {
            songRow.style.opacity = '0';
            setTimeout(() => {
                songRow.remove();
                this.updateStatistics();
            }, 300);
        }
    }

    updateStatistics() {
        // TODO: Recalculate and update statistics
        // This would typically involve making an API call to get updated counts
    }

    initializeTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = document.querySelectorAll('[title]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            }
        });
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-circle' : 
                    'info-circle';
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-${icon} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        }
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    new MyMixesPage();
});

// Export for potential use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MyMixesPage;
}