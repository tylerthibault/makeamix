/**
 * Create Mix Page JavaScript
 * Handles form validation, file uploads, and dynamic interactions
 */

class CreateMixPage {
    constructor() {
        this.init();
    }

    init() {
        this.bindFormEvents();
        this.bindFileUploadEvents();
        this.setupModalValidation();
    }

    bindFormEvents() {
        // Create Mix Form
        const createMixForm = document.getElementById('createMixForm');
        if (createMixForm) {
            createMixForm.addEventListener('submit', (e) => this.handleCreateMixSubmit(e));
        }

        // Upload Song Form
        const uploadSongForm = document.getElementById('uploadSongForm');
        if (uploadSongForm) {
            uploadSongForm.addEventListener('submit', (e) => this.handleUploadSongSubmit(e));
        }

        // Auto-fill song title from filename
        const songFileInput = document.getElementById('songFile');
        if (songFileInput) {
            songFileInput.addEventListener('change', (e) => this.handleSongFileChange(e));
        }
    }

    bindFileUploadEvents() {
        // Cover image preview
        const mixCoverInput = document.getElementById('mixCover');
        if (mixCoverInput) {
            mixCoverInput.addEventListener('change', (e) => this.handleCoverImageChange(e));
        }

        // Song file validation
        const songFileInput = document.getElementById('songFile');
        if (songFileInput) {
            songFileInput.addEventListener('change', (e) => this.validateSongFile(e));
        }
    }

    setupModalValidation() {
        // Real-time validation for required fields
        const requiredInputs = document.querySelectorAll('input[required], select[required]');
        requiredInputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }

    handleCreateMixSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        
        // Basic validation
        if (!this.validateCreateMixForm(form)) {
            return;
        }

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-spinner bi-spin me-2"></i>Creating...';
        submitBtn.disabled = true;

        // TODO: Replace with actual API call
        setTimeout(() => {
            this.showSuccessMessage('Mix created successfully!');
            this.resetForm(form);
            this.closeModal('createMixModal');
            
            // Reset button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 2000);
    }

    handleUploadSongSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        
        // Basic validation
        if (!this.validateUploadSongForm(form)) {
            return;
        }

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-spinner bi-spin me-2"></i>Uploading...';
        submitBtn.disabled = true;

        // TODO: Replace with actual API call
        setTimeout(() => {
            this.showSuccessMessage('Song uploaded successfully!');
            this.resetForm(form);
            this.closeModal('uploadSongModal');
            
            // Reset button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 3000);
    }

    handleSongFileChange(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Auto-fill song title if empty
        const songTitleInput = document.getElementById('songTitle');
        if (songTitleInput && !songTitleInput.value.trim()) {
            const fileName = file.name.replace(/\.[^/.]+$/, ""); // Remove extension
            const cleanTitle = fileName.replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            songTitleInput.value = cleanTitle;
        }

        // Try to get audio metadata (if browser supports it)
        this.extractAudioMetadata(file);
    }

    handleCoverImageChange(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Validate image file
        if (!file.type.startsWith('image/')) {
            this.showFieldError(e.target, 'Please select a valid image file');
            e.target.value = '';
            return;
        }

        // Validate file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
            this.showFieldError(e.target, 'Image file must be less than 5MB');
            e.target.value = '';
            return;
        }

        this.clearFieldError(e.target);
    }

    extractAudioMetadata(file) {
        // This would require a library like jsmediatags for full metadata extraction
        // For now, we'll just handle duration if possible
        const audio = document.createElement('audio');
        audio.preload = 'metadata';
        
        audio.onloadedmetadata = () => {
            const duration = this.formatDuration(audio.duration);
            const durationInput = document.getElementById('songDuration');
            if (durationInput) {
                durationInput.value = duration;
            }
        };

        audio.src = URL.createObjectURL(file);
    }

    formatDuration(seconds) {
        if (isNaN(seconds)) return '';
        
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    validateCreateMixForm(form) {
        let isValid = true;
        
        // Validate mix title
        const mixTitle = form.querySelector('#mixTitle');
        if (!mixTitle.value.trim()) {
            this.showFieldError(mixTitle, 'Mix title is required');
            isValid = false;
        } else if (mixTitle.value.trim().length < 3) {
            this.showFieldError(mixTitle, 'Mix title must be at least 3 characters');
            isValid = false;
        }

        return isValid;
    }

    validateUploadSongForm(form) {
        let isValid = true;
        
        // Validate mix selection
        const selectMix = form.querySelector('#selectMix');
        if (!selectMix.value) {
            this.showFieldError(selectMix, 'Please select a mix');
            isValid = false;
        }

        // Validate song file
        const songFile = form.querySelector('#songFile');
        if (!songFile.files.length) {
            this.showFieldError(songFile, 'Please select a song file');
            isValid = false;
        }

        return isValid;
    }

    validateSongFile(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Validate file type
        const allowedTypes = ['audio/mp3', 'audio/wav', 'audio/ogg', 'audio/m4a', 'audio/mpeg'];
        if (!allowedTypes.includes(file.type)) {
            this.showFieldError(e.target, 'Please select a valid audio file (MP3, WAV, OGG, M4A)');
            e.target.value = '';
            return;
        }

        // Validate file size (50MB limit)
        if (file.size > 50 * 1024 * 1024) {
            this.showFieldError(e.target, 'Audio file must be less than 50MB');
            e.target.value = '';
            return;
        }

        this.clearFieldError(e.target);
    }

    validateField(input) {
        if (input.hasAttribute('required') && !input.value.trim()) {
            this.showFieldError(input, `${this.getFieldLabel(input)} is required`);
            return false;
        }
        
        this.clearFieldError(input);
        return true;
    }

    showFieldError(input, message) {
        this.clearFieldError(input);
        
        input.classList.add('is-invalid');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        input.parentNode.appendChild(errorDiv);
    }

    clearFieldError(input) {
        input.classList.remove('is-invalid');
        const errorDiv = input.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    getFieldLabel(input) {
        const label = input.parentNode.querySelector('label');
        return label ? label.textContent.replace('*', '').trim() : 'Field';
    }

    resetForm(form) {
        form.reset();
        
        // Clear any validation errors
        const invalidInputs = form.querySelectorAll('.is-invalid');
        invalidInputs.forEach(input => this.clearFieldError(input));
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    }

    showSuccessMessage(message) {
        // Create toast notification
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-check-circle me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
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
    new CreateMixPage();
});

// Export for potential use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CreateMixPage;
}