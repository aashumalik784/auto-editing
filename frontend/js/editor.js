// Video Editor Functionality

class VideoEditor {
    constructor() {
        this.videoPlayer = document.getElementById('videoPlayer');
        this.playBtn = document.getElementById('playBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        this.videoSeek = document.getElementById('videoSeek');
        this.timeDisplay = document.getElementById('timeDisplay');
        this.processBtn = document.getElementById('processBtn');
        this.previewBtn = document.getElementById('previewBtn');
        this.exportBtn = document.getElementById('exportBtn');
        this.processingStatus = document.getElementById('processingStatus');
        this.processingProgress = document.getElementById('processingProgress');
        this.processingText = document.getElementById('processingText');
        
        this.videoId = this.getVideoIdFromUrl();
        this.timelineSegments = [];
        
        this.init();
    }
    
    init() {
        if (!this.videoPlayer) return;
        
        // Video controls
        this.setupVideoControls();
        
        // Editor controls
        this.setupEditorControls();
        
        // Load video if ID exists
        if (this.videoId) {
            this.loadVideo(this.videoId);
        }
        
        // Volume slider
        const volumeSlider = document.getElementById('musicVolume');
        const volumeValue = document.getElementById('volumeValue');
        if (volumeSlider && volumeValue) {
            volumeSlider.addEventListener('input', (e) => {
                volumeValue.textContent = e.target.value + '%';
            });
        }
    }
    
    setupVideoControls() {
        // Play button
        if (this.playBtn) {
            this.playBtn.addEventListener('click', () => {                this.videoPlayer.play();
            });
        }
        
        // Pause button
        if (this.pauseBtn) {
            this.pauseBtn.addEventListener('click', () => {
                this.videoPlayer.pause();
            });
        }
        
        // Seek bar
        if (this.videoSeek) {
            this.videoSeek.addEventListener('input', (e) => {
                const time = (e.target.value / 100) * this.videoPlayer.duration;
                this.videoPlayer.currentTime = time;
            });
        }
        
        // Time update
        this.videoPlayer.addEventListener('timeupdate', () => {
            const current = this.videoPlayer.currentTime;
            const duration = this.videoPlayer.duration;
            
            if (this.videoSeek && duration) {
                this.videoSeek.value = (current / duration) * 100;
            }
            
            if (this.timeDisplay) {
                this.timeDisplay.textContent = `${formatTime(current)} / ${formatTime(duration)}`;
            }
        });
    }
    
    setupEditorControls() {
        // Process button
        if (this.processBtn) {
            this.processBtn.addEventListener('click', () => {
                this.processVideo();
            });
        }
        
        // Preview button
        if (this.previewBtn) {
            this.previewBtn.addEventListener('click', () => {
                this.previewChanges();
            });
        }
        
        // Export button        if (this.exportBtn) {
            this.exportBtn.addEventListener('click', () => {
                this.exportVideo();
            });
        }
    }
    
    async loadVideo(videoId) {
        try {
            const response = await API.getVideo(videoId);
            
            if (response.success) {
                this.videoPlayer.src = response.videoUrl;
                this.videoPlayer.load();
                showNotification('Video loaded successfully', 'success');
            }
        } catch (error) {
            console.error('Error loading video:', error);
            showNotification('Failed to load video', 'error');
        }
    }
    
    async processVideo() {
        if (!this.videoId) {
            showNotification('No video selected', 'error');
            return;
        }
        
        // Get processing options
        const options = {
            autoTrim: document.getElementById('autoTrim')?.checked || false,
            autoCaptions: document.getElementById('autoCaptions')?.checked || false,
            autoMusic: document.getElementById('autoMusic')?.checked || false,
            autoColor: document.getElementById('autoColor')?.checked || false,
            musicType: document.getElementById('musicSelect')?.value || 'none',
            musicVolume: document.getElementById('musicVolume')?.value || 20,
            quality: document.getElementById('qualitySelect')?.value || '1080p',
            format: document.getElementById('formatSelect')?.value || 'mp4'
        };
        
        // Show processing status
        this.showProcessingStatus();
        
        try {
            const response = await API.processVideo(this.videoId, options);
            
            if (response.success) {
                // Start polling for progress
                this.pollProcessingStatus(response.jobId);
            } else {                throw new Error(response.message || 'Processing failed');
            }
        } catch (error) {
            console.error('Processing error:', error);
            showNotification('Processing failed: ' + error.message, 'error');
            this.hideProcessingStatus();
        }
    }
    
    async pollProcessingStatus(jobId) {
        const pollInterval = setInterval(async () => {
            try {
                const status = await API.getProcessingStatus(jobId);
                
                if (status.success) {
                    this.updateProcessingProgress(status.progress, status.message);
                    
                    if (status.status === 'completed') {
                        clearInterval(pollInterval);
                        this.hideProcessingStatus();
                        showNotification('Video processing completed!', 'success');
                        
                        // Enable export button
                        if (this.exportBtn) {
                            this.exportBtn.disabled = false;
                        }
                        
                        // Load processed video
                        this.loadVideo(this.videoId);
                    } else if (status.status === 'failed') {
                        clearInterval(pollInterval);
                        this.hideProcessingStatus();
                        showNotification('Processing failed: ' + status.message, 'error');
                    }
                }
            } catch (error) {
                console.error('Polling error:', error);
            }
        }, 2000); // Poll every 2 seconds
    }
    
    async previewChanges() {
        showNotification('Preview feature coming soon!', 'info');
    }
    
    async exportVideo() {
        try {
            const response = await API.exportVideo(this.videoId);
            
            if (response.success) {                // Download the video
                const link = document.createElement('a');
                link.href = response.downloadUrl;
                link.download = `edited_video_${this.videoId}.${response.format}`;
                link.click();
                
                showNotification('Video exported successfully!', 'success');
            }
        } catch (error) {
            console.error('Export error:', error);
            showNotification('Export failed: ' + error.message, 'error');
        }
    }
    
    showProcessingStatus() {
        if (this.processingStatus) {
            this.processingStatus.style.display = 'block';
        }
    }
    
    hideProcessingStatus() {
        if (this.processingStatus) {
            this.processingStatus.style.display = 'none';
        }
    }
    
    updateProcessingProgress(percent, message) {
        if (this.processingProgress) {
            this.processingProgress.style.width = percent + '%';
        }
        if (this.processingText) {
            this.processingText.textContent = message;
        }
    }
    
    getVideoIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('video');
    }
}

// Initialize editor
const editor = new VideoEditor();
