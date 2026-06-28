function openUploadModal() {
    document.getElementById('uploadModal').style.display = 'flex';
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('uploadProgress').style.display = 'none';
    document.getElementById('progressFill').style.width = '0%';
}

document.getElementById('videoInput').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (file) {
        await uploadVideo(file);
    }
});

async function uploadVideo(file) {
    document.getElementById('uploadArea').style.display = 'none';
    document.getElementById('uploadProgress').style.display = 'block';

    const formData = new FormData();
    formData.append('video', file);

    try {
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                document.getElementById('progressFill').style.width = percent + '%';
                document.getElementById('progressText').textContent = 'Uploading... ' + percent + '%';
            }
        });

        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                const response = JSON.parse(xhr.responseText);
                alert('Upload successful!');
                closeUploadModal();
                loadProjects();
            } else {
                alert('Upload failed');
                closeUploadModal();
            }
        });

        xhr.addEventListener('error', () => {
            alert('Upload error');
            closeUploadModal();
        });

        xhr.open('POST', 'https://auto-editing.onrender.com/api/upload');
        xhr.send(formData);
    } catch (error) {
        alert('Error: ' + error.message);
        closeUploadModal();
    }
}

async function loadProjects() {
    try {
        const response = await API.getProjects();
        const projectsList = document.getElementById('projectsList');
        
        if (response.success && response.projects && response.projects.length > 0) {
            projectsList.innerHTML = response.projects.map(project => `
                <div class="project-item" onclick="window.location.href='editor.html?project=${project.id}'">
                    <div class="project-thumbnail">
                        <i class="fas fa-video"></i>
                    </div>
                    <div class="project-info">
                        <h3>${project.name}</h3>
                        <p class="project-date">${project.size} - ${project.status}</p>
                    </div>
                    <div class="project-menu" onclick="event.stopPropagation(); deleteProject('${project.id}')">
                        <i class="fas fa-ellipsis-v"></i>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

async function deleteProject(projectId) {
    if (confirm('Delete this project?')) {
        try {
            const response = await API.deleteProject(projectId);
            if (response.success) {
                alert('Project deleted');
                loadProjects();
            }
        } catch (error) {
            alert('Delete failed');
        }
    }
}

window.onclick = function(event) {
    const modal = document.getElementById('uploadModal');
    if (event.target == modal) {
        closeUploadModal();
    }
}

window.addEventListener('DOMContentLoaded', loadProjects);
