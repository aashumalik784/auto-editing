// Global variables
let currentProjectId = null;
let currentVideoId = null;

// Modal Functions
function openUploadModal() {
    document.getElementById('uploadModal').style.display = 'flex';
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
    resetUploadForm();
}

function resetUploadForm() {
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('uploadProgress').style.display = 'none';
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('progressText').textContent = 'Uploading... 0%';
    document.getElementById('videoInput').value = '';
}

// Tool Functions
function openPhotoEditor() {
    alert('Photo Editor - Coming Soon!');
    // window.location.href = 'photo-editor.html';
}

function openAutoCut() {
    window.location.href = 'editor.html?tool=autocut';
}

function openRetouch() {
    alert('Retouch Tool - Coming Soon!');
}

function openAIGenerator() {
    alert('AI Generator - Coming Soon!');
}

function openAutoCaptions() {
    window.location.href = 'editor.html?tool=captions';
}

function openDesktopEditor() {
    alert('Desktop Editor - Download our desktop app!');
}

function openRemoveBackground() {
    alert('Remove Background - Coming Soon!');
}

function openCamera() {
    alert('Camera - Coming Soon!');
}

function openAllTools() {
    alert('All Tools - Full list coming soon!');
}

function showSettings() {
    alert('Settings - Coming Soon!');
}

// File Upload Handling
document.addEventListener('DOMContentLoaded', function() {
    const videoInput = document.getElementById('videoInput');
    const uploadArea = document.getElementById('uploadArea');
    
    if (videoInput) {
        videoInput.addEventListener('change', handleFileSelect);
    }
    
    if (uploadArea) {
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
    }
    
    // Load projects on page load
    loadProjects();
});

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.style.borderColor = '#667eea';
    e.currentTarget.style.background = '#f0f4ff';
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.style.borderColor = '';
    e.currentTarget.style.background = '';
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.style.borderColor = '';
    e.currentTarget.style.background = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
}

async function handleFileUpload(file) {
    // Validate file
    if (!file.type.startsWith('video/')) {
        alert('Please upload a video file');
        return;
    }
    
    if (file.size > 500 * 1024 * 1024) {
        alert('File size must be less than 500MB');
        return;
    }
    
    // Show progress
    document.getElementById('uploadArea').style.display = 'none';
    document.getElementById('uploadProgress').style.display = 'block';
    
    try {
        const formData = new FormData();
        formData.append('video', file);
        
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                document.getElementById('progressFill').style.width = percent + '%';
                document.getElementById('progressText').textContent = `Uploading... ${percent}%`;
            }
        });
        
        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                const response = JSON.parse(xhr.responseText);
                handleUploadSuccess(response);
            } else {
                throw new Error('Upload failed');
            }
        });
        
        xhr.addEventListener('error', () => {
            alert('Upload failed. Please try again.');
            resetUploadForm();
        });
        
        xhr.open('POST', 'https://auto-editing.onrender.com/api/upload');
        xhr.send(formData);
        
    } catch (error) {
        console.error('Upload error:', error);
        alert('Upload failed: ' + error.message);
        resetUploadForm();
    }
}

async function handleUploadSuccess(response) {
    alert('Video uploaded successfully!');
    closeUploadModal();
    
    // Reload projects
    await loadProjects();
    
    // Ask if user wants to edit
    if (confirm('Video uploaded! Do you want to edit it now?')) {
        window.location.href = `editor.html?project=${response.projectId}&video=${response.videoId}`;
    }
}

// Load Projects
async function loadProjects() {
    try {
        const response = await API.getProjects();
        if (response.success) {
            displayProjects(response.projects);
        }
    } catch (error) {
        console.error('Error loading projects:', error);
        document.getElementById('projectsList').innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error loading projects</p>
            </div>
        `;
    }
}

function displayProjects(projects) {
    const projectsList = document.getElementById('projectsList');
    
    if (!projects || projects.length === 0) {
        projectsList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-folder-open"></i>
                <p>No projects yet</p>
                <button class="create-btn" onclick="openUploadModal()">
                    Create your first video
                </button>
            </div>
        `;
        return;
    }
    
    projectsList.innerHTML = projects.map(project => `
        <div class="project-item" onclick="openProject('${project.id}')">
            <div class="project-thumbnail">
                <i class="fas fa-video"></i>
            </div>
            <div class="project-info">
                <h3>${project.name || 'Untitled Project'}</h3>
                <p class="project-date">${new Date(project.created_at).toLocaleString()}</p>
                <p class="project-size">
                    <i class="fas fa-database"></i> ${project.size || '0MB'} 
                    <span class="status-badge ${project.status}">${project.status}</span>
                </p>
            </div>
            <div class="project-menu" onclick="event.stopPropagation(); showProjectMenu('${project.id}')">
                <i class="fas fa-ellipsis-v"></i>
            </div>
        </div>
    `).join('');
}

function openProject(projectId) {
    window.location.href = `editor.html?project=${projectId}`;
}

function showProjectMenu(projectId) {
    const menu = confirm('Delete this project?');
    if (menu) {
        deleteProject(projectId);
    }
}

async function deleteProject(projectId) {
    try {
        const response = await API.deleteProject(projectId);
        if (response.success) {
            alert('Project deleted successfully');
            await loadProjects();
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('Failed to delete project');
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('uploadModal');
    if (event.target == modal) {
        closeUploadModal();
    }
}
