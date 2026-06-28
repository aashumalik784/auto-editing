// Video Upload Handler

class VideoUploader {
    constructor() {
        this.uploadArea = document.getElementById('uploadArea');
        this.videoInput = document.getElementById('videoInput');
        this.uploadProgress = document.getElementById('uploadProgress');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        
        this.maxFileSize = 500 * 1024 * 1024; // 500MB
        this.allowedTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska'];
        
        this.init();
    }
    
    init() {
        if (!this.uploadArea) return;
        
        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        // File input change
        if (this.videoInput) {
            this.videoInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.add('dragover');
        this.uploadArea.style.borderColor = 'var(--primary-color)';
        this.uploadArea.style.background = '#f0f0ff';
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.remove('dragover');
        this.uploadArea.style.borderColor = '';
        this.uploadArea.style.background = '';
    }
    
    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.remove('dragover');        this.uploadArea.style.borderColor = '';
        this.uploadArea.style.background = '';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }
    
    async processFile(file) {
        // Validate file
        if (!this.validateFile(file)) {
            return;
        }
        
        // Show progress
        this.showProgress();
        
        try {
            // Upload file
            const result = await this.uploadFile(file);
            
            if (result.success) {
                showNotification('Video uploaded successfully!', 'success');
                
                // Redirect to editor with video ID
                setTimeout(() => {
                    window.location.href = `editor.html?video=${result.videoId}`;
                }, 1000);
            } else {
                throw new Error(result.message || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showNotification('Upload failed: ' + error.message, 'error');
            this.hideProgress();
        }
    }
    
    validateFile(file) {
        // Check file size
        if (file.size > this.maxFileSize) {
            showNotification('File size exceeds 500MB limit', 'error');            return false;
        }
        
        // Check file type
        if (!this.allowedTypes.includes(file.type)) {
            showNotification('Invalid file type. Please upload MP4, AVI, MOV, or MKV', 'error');
            return false;
        }
        
        return true;
    }
    
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('video', file);
        
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            // Upload progress
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    this.updateProgress(percent);
                }
            });
            
            // Upload complete
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (e) {
                        reject(new Error('Invalid response'));
                    }
                } else {
                    reject(new Error(`Upload failed with status ${xhr.status}`));
                }
            });
            
            // Upload error
            xhr.addEventListener('error', () => {
                reject(new Error('Network error during upload'));
            });
            
            // Upload abort
            xhr.addEventListener('abort', () => {
                reject(new Error('Upload cancelled'));
            });            
            // Open and send request
            xhr.open('POST', `${API_BASE_URL}/upload`);
            xhr.send(formData);
        });
    }
    
    showProgress() {
        if (this.uploadProgress) {
            this.uploadProgress.style.display = 'block';
            this.uploadArea.style.display = 'none';
        }
    }
    
    hideProgress() {
        if (this.uploadProgress) {
            this.uploadProgress.style.display = 'none';
            this.uploadArea.style.display = 'block';
        }
    }
    
    updateProgress(percent) {
        if (this.progressFill) {
            this.progressFill.style.width = percent + '%';
        }
        if (this.progressText) {
            this.progressText.textContent = percent + '%';
        }
    }
}

// Initialize uploader
const uploader = new VideoUploader();
