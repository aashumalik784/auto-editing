const API_BASE_URL = 'https://auto-editing.onrender.com'; // Slash nahi lagana end me

async function uploadVideo(file) {
    const formData = new FormData();
    formData.append('video', file);

    try {
        const response = await fetch(`${API_BASE_URL}/api/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Upload failed with status ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
}

async function processVideo(videoId, options) {
    const response = await fetch(`${API_BASE_URL}/api/process`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            videoId: videoId,
            options: options
        }),
    });
    return await response.json();
}

async function getStatus(jobId) {
    const response = await fetch(`${API_BASE_URL}/api/status/${jobId}`);
    return await response.json();
}

async function getVideoUrl(videoId) {
    const response = await fetch(`${API_BASE_URL}/api/video/${videoId}`);
    const data = await response.json();
    return `${API_BASE_URL}${data.videoUrl}`; // Full URL return karega
}
