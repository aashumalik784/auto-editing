from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List
import uuid
import os
import shutil
from datetime import datetime

app = FastAPI(title="Auto-Editing API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = "/tmp/uploads"
PROCESSED_DIR = "/tmp/processed"
TEMP_DIR = "/tmp/temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

processing_jobs = {}
projects_db = {}

class ProcessRequest(BaseModel):
    videoId: str
    options: Dict

@app.get("/")
async def root():
    return {"status": "healthy", "service": "Auto-Editing API", "version": "1.0.0"}

@app.post("/api/upload")
async def upload_video(video: UploadFile = File(...)):
    if not video.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    video_id = str(uuid.uuid4())
    file_extension = os.path.splitext(video.filename)[1] or '.mp4'
    file_path = os.path.join(UPLOAD_DIR, f"{video_id}{file_extension}")
    with open(file_path, 'wb') as buffer:
        content = await video.read()
        buffer.write(content)
    
    project_id = str(uuid.uuid4())
    projects_db[project_id] = {
        "id": project_id,
        "video_id": video_id,
        "name": video.filename,
        "created_at": datetime.now().isoformat(),
        "size": f"{len(content) / (1024*1024):.1f}MB",
        "status": "uploaded",        "duration": "00:00"
    }
    
    return {"success": True, "videoId": video_id, "projectId": project_id, "message": "Video uploaded successfully"}

@app.get("/api/video/{video_id}")
async def get_video(video_id: str):
    video_path = None
    for ext in ['.mp4', '.avi', '.mov', '.mkv']:
        test_path = os.path.join(UPLOAD_DIR, f"{video_id}{ext}")
        if os.path.exists(test_path):
            video_path = test_path
            break
    if not video_path:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"success": True, "videoUrl": f"/api/video/{video_id}/file", "video": {"id": video_id, "filename": os.path.basename(video_path)}}

@app.get("/api/video/{video_id}/file")
async def get_video_file(video_id: str):
    video_path = None
    for ext in ['.mp4', '.avi', '.mov', '.mkv']:
        test_path = os.path.join(UPLOAD_DIR, f"{video_id}{ext}")
        if os.path.exists(test_path):
            video_path = test_path
            break
    if not video_path:
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(video_path, media_type="video/mp4")

@app.post("/api/process")
async def process_video(request: ProcessRequest, background_tasks: BackgroundTasks):
    video_id = request.videoId
    options = request.options
    job_id = str(uuid.uuid4())
    processing_jobs[job_id] = {"id": job_id, "video_id": video_id, "status": "processing", "progress": 0, "message": "Starting processing...", "options": options, "created_at": datetime.now().isoformat()}
    background_tasks.add_task(process_video_task, job_id, video_id, options)
    return {"success": True, "jobId": job_id, "message": "Processing started"}

async def process_video_task(job_id: str, video_id: str, options: Dict):
    input_path = None
    for ext in ['.mp4', '.avi', '.mov', '.mkv']:
        test_path = os.path.join(UPLOAD_DIR, f"{video_id}{ext}")
        if os.path.exists(test_path):
            input_path = test_path
            break
    if not input_path:
        processing_jobs[job_id]["status"] = "failed"
        return
    output_path = os.path.join(PROCESSED_DIR, f"{video_id}_edited.mp4")
    processing_jobs[job_id]["progress"] = 50    shutil.copy(input_path, output_path)
    processing_jobs[job_id]["status"] = "completed"
    processing_jobs[job_id]["progress"] = 100
    processing_jobs[job_id]["message"] = "Processing completed"
    processing_jobs[job_id]["output_path"] = output_path

@app.get("/api/status/{job_id}")
async def get_processing_status(job_id: str):
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = processing_jobs[job_id]
    return {"success": True, "status": job["status"], "progress": job["progress"], "message": job["message"]}

@app.post("/api/export/{video_id}")
async def export_video(video_id: str):
    output_path = os.path.join(PROCESSED_DIR, f"{video_id}_edited.mp4")
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Processed video not found")
    return {"success": True, "downloadUrl": f"/api/download/{video_id}", "format": "mp4"}

@app.get("/api/download/{video_id}")
async def download_video(video_id: str):
    output_path = os.path.join(PROCESSED_DIR, f"{video_id}_edited.mp4")
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(output_path, media_type="video/mp4", filename=f"edited_video_{video_id}.mp4")

@app.get("/api/projects")
async def get_projects():
    projects_list = list(projects_db.values())
    total = len(projects_list)
    processed = len([p for p in projects_list if p.get("status") == "completed"])
    pending = len([p for p in projects_list if p.get("status") == "uploaded"])
    storage = f"{sum(len(os.listdir(UPLOAD_DIR)) * 0.5, 0):.1f}MB"
    return {"success": True, "projects": projects_list, "stats": {"total": total, "processed": processed, "pending": pending, "storage": storage}}

@app.delete("/api/project/{project_id}")
async def delete_project(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    project = projects_db[project_id]
    video_id = project.get("video_id")
    for folder in [UPLOAD_DIR, PROCESSED_DIR, TEMP_DIR]:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.startswith(video_id) or file.startswith(project_id):
                    os.remove(os.path.join(folder, file))
    del projects_db[project_id]
    return {"success": True, "message": "Project deleted successfully"}
@app.get("/api/stats")
async def get_user_stats():
    total = len(projects_db)
    return {"success": True, "stats": {"total_videos": total, "total_processing_time": 0, "storage_used": 0}}
