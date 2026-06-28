// API Handler

const API_BASE_URL = 'http://localhost:8000'; // Change this to your backend URL

const API = {
    // Upload video
    async uploadVideo(file) {
        const formData = new FormData();
        formData.append('video', file);
        
        const response = await fetch(`${API_BASE_URL}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    },
    
    // Get video info
    async getVideo(videoId) {
        const response = await fetch(`${API_BASE_URL}/api/video/${videoId}`);
        return await response.json();
    },
    
    // Process video
    async processVideo(videoId, options) {
        const response = await fetch(`${API_BASE_URL}/api/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                videoId: videoId,
                options: options
            })
        });
        
        return await response.json();
    },
    
    // Get processing status
    async getProcessingStatus(jobId) {
        const response = await fetch(`${API_BASE_URL}/api/status/${jobId}`);
        return await response.json();
    },
    
    // Export video
    async exportVideo(videoId) {
        const response = await fetch(`${API_BASE_URL}/api/export/${videoId}`, {
            method: 'POST'
        });
        
        return await response.json();
    },
    
    // Get all projects
    async getProjects() {
        const response = await fetch(`${API_BASE_URL}/api/projects`);
        return await response.json();
    },
    
    // Delete project
    async deleteProject(projectId) {
        const response = await fetch(`${API_BASE_URL}/api/project/${projectId}`, {
            method: 'DELETE'
        });
        
        return await response.json();
    },
    
    // Get user stats
    async getUserStats() {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        return await response.json();
    }
};
