const API_BASE_URL = 'https://auto-editing.onrender.com';

const API = {
    async uploadVideo(file) {
        const formData = new FormData();
        formData.append('video', file);
        const response = await fetch(API_BASE_URL + '/api/upload', {
            method: 'POST',
            body: formData
        });
        return await response.json();
    },
    
    async getProjects() {
        const response = await fetch(API_BASE_URL + '/api/projects');
        return await response.json();
    },
    
    async deleteProject(projectId) {
        const response = await fetch(API_BASE_URL + '/api/project/' + projectId, {
            method: 'DELETE'
        });
        return await response.json();
    },
    
    async processVideo(videoId, options) {
        const response = await fetch(API_BASE_URL + '/api/process', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({videoId: videoId, options: options})
        });
        return await response.json();
    },
    
    async getProcessingStatus(jobId) {
        const response = await fetch(API_BASE_URL + '/api/status/' + jobId);
        return await response.json();
    }
};
