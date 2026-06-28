// Load projects from backend
async function loadProjects() {
    try {
        const response = await API.getProjects();
        if (response.success) {
            displayProjects(response.projects);
        }
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

function displayProjects(projects) {
    const projectsList = document.getElementById('projectsList');
    if (!projectsList) return;
    
    if (!projects || projects.length === 0) {
        projectsList.innerHTML = `
            <div class="empty-projects">
                <i class="fas fa-folder-open"></i>
                <p>No projects yet</p>
                <button onclick="window.location.href='editor.html'" class="create-btn">
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
                <h3>${project.name || 'Untitled'}</h3>
                <p class="project-date">${new Date(project.created_at).toLocaleString()}</p>
                <p class="project-size">
                    <i class="fas fa-cut"></i> ${project.size || '0MB'} | ${project.duration || '00:00'}
                </p>
            </div>
            <div class="project-menu">
                <i class="fas fa-ellipsis-v"></i>
            </div>
        </div>
    `).join('');
}

function openProject(projectId) {
    window.location.href = `editor.html?project=${projectId}`;
}

// Load projects on page load
if (window.location.pathname.includes('index.html') || window.location.pathname === '/') {
    document.addEventListener('DOMContentLoaded', loadProjects);
}
