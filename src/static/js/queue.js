// Global Queue Management System
class QueueManager {
    constructor() {
        this.queue = [];
        this.currentIndex = -1;
        this.audioPlayer = null;
        this.isPlaying = false;
        this.loadQueue();
    }

    // Load queue from localStorage
    loadQueue() {
        const saved = localStorage.getItem('songQueue');
        if (saved) {
            try {
                const data = JSON.parse(saved);
                this.queue = data.queue || [];
                this.currentIndex = data.currentIndex || -1;
            } catch (e) {
                console.error('Failed to load queue:', e);
            }
        }
    }

    // Save queue to localStorage
    saveQueue() {
        localStorage.setItem('songQueue', JSON.stringify({
            queue: this.queue,
            currentIndex: this.currentIndex
        }));
    }

    // Save playback state
    savePlaybackState(currentTime, isPlaying) {
        localStorage.setItem('playbackState', JSON.stringify({
            currentTime: currentTime,
            isPlaying: isPlaying,
            timestamp: Date.now()
        }));
    }

    // Get playback state
    getPlaybackState() {
        const saved = localStorage.getItem('playbackState');
        if (saved) {
            try {
                const state = JSON.parse(saved);
                // Only restore if less than 5 seconds old (prevent stale state)
                if (Date.now() - state.timestamp < 5000) {
                    return state;
                }
            } catch (e) {
                console.error('Failed to load playback state:', e);
            }
        }
        return null;
    }

    // Clear playback state
    clearPlaybackState() {
        localStorage.removeItem('playbackState');
    }

    // Add a single song to queue
    addSong(song) {
        // song should be an object: { id, title, url }
        this.queue.push(song);
        this.saveQueue();
        this.notifyQueueUpdate();
    }

    // Add multiple songs (for playlists)
    addSongs(songs) {
        this.queue.push(...songs);
        this.saveQueue();
        this.notifyQueueUpdate();
    }

    // Play specific song from queue
    playSongAtIndex(index) {
        if (index >= 0 && index < this.queue.length) {
            this.currentIndex = index;
            this.saveQueue();
            const song = this.queue[index];
            
            // Use global audio player instead of redirecting
            const globalAudio = document.getElementById('global-audio-player');
            const globalSource = document.getElementById('global-audio-source');
            
            if (globalAudio && globalSource) {
                console.log('Playing song:', song.title, 'URL:', `/songs/audio/${song.id}`);
                globalSource.src = `/songs/audio/${song.id}`;
                globalAudio.load();
                globalAudio.play()
                    .then(() => console.log('Playback started successfully'))
                    .catch(err => console.error('Play failed:', err));
                this.notifyQueueUpdate();
            } else {
                console.error('Global audio player not found, redirecting');
                // Fallback to redirect if global player not found
                window.location.href = `/songs/${song.id}?fromQueue=true`;
            }
        }
    }

    // Get current song
    getCurrentSong() {
        if (this.currentIndex >= 0 && this.currentIndex < this.queue.length) {
            return this.queue[this.currentIndex];
        }
        return null;
    }

    // Get next song
    getNextSong() {
        if (this.currentIndex < this.queue.length - 1) {
            return this.queue[this.currentIndex + 1];
        }
        return null;
    }

    // Get previous song
    getPreviousSong() {
        if (this.currentIndex > 0) {
            return this.queue[this.currentIndex - 1];
        }
        return null;
    }

    // Play next song
    playNext() {
        const next = this.getNextSong();
        if (next) {
            this.playSongAtIndex(this.currentIndex + 1);
        }
    }

    // Play previous song
    playPrevious() {
        const prev = this.getPreviousSong();
        if (prev) {
            this.playSongAtIndex(this.currentIndex - 1);
        }
    }

    // Remove song from queue
    removeSong(index) {
        if (index >= 0 && index < this.queue.length) {
            this.queue.splice(index, 1);
            if (this.currentIndex >= index) {
                this.currentIndex = Math.max(-1, this.currentIndex - 1);
            }
            this.saveQueue();
            this.notifyQueueUpdate();
        }
    }

    // Clear entire queue
    clearQueue() {
        this.queue = [];
        this.currentIndex = -1;
        this.saveQueue();
        this.notifyQueueUpdate();
    }

    // Get all songs in queue
    getQueue() {
        return this.queue;
    }

    // Get queue length
    getQueueLength() {
        return this.queue.length;
    }

    // Set current song by ID (for when navigating directly)
    setCurrentSongById(songId) {
        const index = this.queue.findIndex(s => s.id == songId);
        if (index >= 0) {
            this.currentIndex = index;
            this.saveQueue();
            this.notifyQueueUpdate();
        }
    }

    // Notify UI of queue updates
    notifyQueueUpdate() {
        window.dispatchEvent(new CustomEvent('queueUpdated', {
            detail: {
                queue: this.queue,
                currentIndex: this.currentIndex,
                length: this.queue.length
            }
        }));
    }

    // Replace entire queue (for playing a playlist from start)
    replaceQueue(songs, startIndex = 0) {
        this.queue = songs;
        this.currentIndex = startIndex;
        this.saveQueue();
        this.notifyQueueUpdate();
        if (songs.length > 0) {
            this.playSongAtIndex(startIndex);
        }
    }
}

// Create global instance
window.queueManager = new QueueManager();
