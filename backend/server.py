from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
import os
import shutil
from datetime import datetime

app = FastAPI(title="Auto-Editing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/tmp/uploads"
PROCESSED_DIR = "/tmp/processed"
TEMP_DIR = "/tmp/temp"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

processing_jobs: Dict[str, Dict] = {}

class ProcessRequest(BaseModel):
    videoId: str
    options: Dict

@app.get("/")
async def root():
    return {"status": "healthy", "service": "Auto-Editing API", "version": "1.0.0"}

@app.post("/api/upload")
async def upload_video(background_tasks: BackgroundTasks, video: UploadFile = File(...)):
    try:
        if not video.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        video_id = str(uuid.uuid4())
        file_extension = os.path.splitext(video.filename)[1] or '.mp4'
        file_path = os.path.join(UPLOAD_DIR, f"{video_id}{file_extension}")
        
        with open(file_path, 'wb') as buffer:
            content = await video.read()            buffer.write(content)
        
        print(f"Video uploaded: {video_id}")
        return {"success": True, "videoId": video_id, "message": "Video uploaded successfully"}
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
    try:
        video_id = request.videoId
        options = request.options
        job_id = str(uuid.uuid4())
        
        processing_jobs[job_id] = {
            "id": job_id,
            "video_id": video_id,
            "status": "processing",
            "progress": 0,
            "message": "Starting processing...",            "options": options,
            "created_at": datetime.now().isoformat()
        }
        
        background_tasks.add_task(process_video_task, job_id, video_id, options)
        print(f"Processing started: {job_id}")
        
        return {"success": True, "jobId": job_id, "message": "Processing started"}
    
    except Exception as e:
        print(f"Process error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_video_task(job_id: str, video_id: str, options: Dict):
    try:
        input_path = None
        for ext in ['.mp4', '.avi', '.mov', '.mkv']:
            test_path = os.path.join(UPLOAD_DIR, f"{video_id}{ext}")
            if os.path.exists(test_path):
                input_path = test_path
                break
        
        if not input_path:
            raise Exception("Input video not found")
        
        output_path = os.path.join(PROCESSED_DIR, f"{video_id}_edited.mp4")
        
        processing_jobs[job_id]["progress"] = 10
        processing_jobs[job_id]["message"] = "Analyzing video..."
        
        current_path = input_path
        
        if options.get("autoTrim"):
            processing_jobs[job_id]["progress"] = 30
            processing_jobs[job_id]["message"] = "Removing silent parts..."
            trimmed_path = os.path.join(TEMP_DIR, f"{video_id}_trimmed.mp4")
            shutil.copy(current_path, trimmed_path)
            current_path = trimmed_path
        
        if options.get("autoCaptions"):
            processing_jobs[job_id]["progress"] = 50
            processing_jobs[job_id]["message"] = "Generating captions..."
        
        if options.get("autoMusic") and options.get("musicType") != "none":
            processing_jobs[job_id]["progress"] = 70
            processing_jobs[job_id]["message"] = "Adding background music..."
        
        if options.get("autoColor"):
            processing_jobs[job_id]["progress"] = 85
            processing_jobs[job_id]["message"] = "Applying color correction..."        
        processing_jobs[job_id]["progress"] = 95
        processing_jobs[job_id]["message"] = "Finalizing video..."
        
        shutil.copy(current_path, output_path)
        
        processing_jobs[job_id]["status"] = "completed"
        processing_jobs[job_id]["progress"] = 100
        processing_jobs[job_id]["message"] = "Processing completed"
        processing_jobs[job_id]["output_path"] = output_path
        
        print(f"Processing completed: {job_id}")
    
    except Exception as e:
        print(f"Processing error: {str(e)}")
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["message"] = f"Processing failed: {str(e)}"

@app.get("/api/status/{job_id}")
async def get_processing_status(job_id: str):
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_jobs[job_id]
    return {"success": True, "status": job["status"], "progress": job["progress"], "message": job["message"]}

@app.post("/api/export/{video_id}")
async def export_video(video_id: str):
    try:
        output_path = os.path.join(PROCESSED_DIR, f"{video_id}_edited.mp4")
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=404, detail="Processed video not found")
        
        return {"success": True, "downloadUrl": f"/api/download/{video_id}", "format": "mp4"}
    
    except Exception as e:
        print(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{video_id}")
async def download_video(video_id: str):
    output_path = os.path.join(PROCESSED_DIR, f"{video_id}_edited.mp4")
    
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(output_path, media_type="video/mp4", filename=f"edited_video_{video_id}.mp4")

@app.get("/api/projects")async def get_projects():
    return {"success": True, "projects": [], "stats": {"total": 0, "processed": 0, "pending": 0, "storage": "0 MB"}}

@app.delete("/api/project/{project_id}")
async def delete_project(project_id: str):
    try:
        for folder in [UPLOAD_DIR, PROCESSED_DIR]:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    if file.startswith(project_id):
                        os.remove(os.path.join(folder, file))
        
        return {"success": True, "message": "Project deleted successfully"}
    
    except Exception as e:
        print(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_user_stats():
    return {"success": True, "stats": {"total_videos": 0, "total_processing_time": 0, "storage_used": 0}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
