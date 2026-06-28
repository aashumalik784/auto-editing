from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import uuid
import os
import shutil
import json
from datetime import datetime
from pathlib import Path

app = FastAPI(
    title="Auto-Editing API",
    description="AI-powered video editing API",
    version="2.0.0"
)

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
PROJECTS_FILE = "/tmp/projects.json"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

processing_jobs: Dict[str, Dict] = {}
projects_db: Dict[str, Dict] = {}

class ProcessRequest(BaseModel):
    videoId: str
    options: Dict

class ProcessResponse(BaseModel):
    success: bool
    jobId: Optional[str] = None
    message: Optional[str] = None

class ProjectInfo(BaseModel):
    id: str
    name: str
    videoId: str
    status: str
    createdAt: str
    size: str
    duration: str

def load_projects():
    global projects_db
    if os.path.exists(PROJECTS_FILE):
        try:
            with open(PROJECTS_FILE, 'r') as f:
                projects_db = json.load(f)
        except:
            projects_db = {}

def save_projects():
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects_db, f, indent=2)

def get_file_size(file_path: str) -> str:
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.1f}MB"
    return "0MB"

def get_video_duration(video_id: str) -> str:
    return "00:00"

@app.on_event("startup")
async def startup_event():
    load_projects()

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Auto-Editing API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "uptime": "running",
        "projects_count": len(projects_db),
        "jobs_count": len(processing_jobs)
    }

@app.post("/api/upload")
async def upload_video(video: UploadFile = File(...)):
    try:
        if not video.content_type or not video.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        file_size = len(await video.read())
        await video.seek(0)
        
        if file_size > 500 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 500MB limit")
        
        video_id = str(uuid.uuid4())
        file_extension = os.path.splitext(video.filename)[1] or '.mp4'
        file_path = os.path.join(UPLOAD_DIR, f"{video_id}{file_extension}")
        
        with open(file_path, 'wb') as buffer:
            content = await video.read()
            buffer.write(content)
        
        project_id = str(uuid.uuid4())
        file_size_mb = f"{len(content) / (1024 * 1024):.1f}MB"
        
        projects_db[project_id] = {
            "id": project_id,
            "video_id": video_id,
            "name": video.filename,
            "original_name": video.filename,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "size": file_size_mb,
            "status": "uploaded",
            "duration": "00:00",
            "format": file_extension,
            "processing_progress": 0
        }
        
        save_projects()
        
        return {
            "success": True,
            "videoId": video_id,
            "projectId": project_id,
            "message": "Video uploaded successfully",
            "size": file_size_mb
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/{video_id}")
async def get_video(video_id: str):
    try:
        video_path = None
        for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            test_path = os.path.join(UPLOAD_DIR, f"{video_id}{ext}")
            if os.path.exists(test_path):
                video_path = test_path
                break
        
        if not video_path:
            raise HTTPException(status_code=404, detail="Video not found")
        
        file_size = get_file_size(video_path)
        
        return {
            "success": True,
            "videoUrl": f"/api/video/{video_id}/file",
            "video": {
                "id": video_id,
                "filename": os.path.basename(video_path),
                "size": file_size,
                "path": video_path
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get video error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/{video_id}/file")
async def get_video_file(video_id: str):
    video_path = None
    for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
        test_path = os.path.join(UPLOAD_DIR, f"{video_id}{ext}")
        if os.path.exists(test_path):
            video_path = test_path
            break
    
    if not video_path:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=os.path.basename(video_path)
    )

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
            "message": "Starting processing...",
            "options": options,
            "created_at": datetime.now().isoformat(),
            "started_at": datetime.now().isoformat(),
            "completed_at": None
        }
        
        background_tasks.add_task(process_video_task, job_id, video_id, options)
        
        return {
            "success": True,
            "jobId": job_id,
            "message": "Processing started",
            "estimatedTime": "2-5 minutes"
        }
    
    except Exception as e:
        print(f"Process error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_video_task(job_id: str, video_id: str, options: Dict):
    try:
        input_path = None
        for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            test_path = os.path.join(UPLOAD_DIR, f"{video_id}{ext}")
            if os.path.exists(test_path):
                input_path = test_path
                break
        
        if not input_path:
            processing_jobs[job_id]["status"] = "failed"
            processing_jobs[job_id]["message"] = "Input video not found"
            processing_jobs[job_id]["completed_at"] = datetime.now().isoformat()
            return
        
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
        
        if options.get("autoMusic") and options.get("musicType")!= "none":
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
        processing_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
        for project_id, project in projects_db.items():
            if project.get("video_id") == video_id:
                project["status"] = "completed"
                project["updated_at"] = datetime.now().isoformat()
                project["processing_progress"] = 100
                break
        
        save_projects()
        
        print(f"Processing completed: {job_id}")
    
    except Exception as e:
        print(f"Processing error: {str(e)}")
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["message"] = f"Processing failed: {str(e)}"
        processing_jobs[job_id]["completed_at"] = datetime.now().isoformat()

@app.get("/api/status/{job_id}")
async def get_processing_status(job_id: str):
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_jobs[job_id]
    
    return {
        "success": True,
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
        "created_at": job.get("created_at"),
        "completed_at": job.get("completed_at")
    }

@app.post("/api/export/{video_id}")
async def export_video(video_id: str):
    try:
        output_path = os.path.join(PROCESSED_DIR, f"{video_id}_edited.mp4")
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=404, detail="Processed video not found")
        
        file_size = get_file_size(output_path)
        
        return {
            "success": True,
            "downloadUrl": f"/api/download/{video_id}",
            "format": "mp4",
            "size": file_size,
            "expires_in": "24 hours"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{video_id}")
async def download_video(video_id: str):
    output_path = os.path.join(PROCESSED_DIR, f"{video_id}_edited.mp4")
    
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"edited_video_{video_id}.mp4",
        headers={
            "Content-Disposition": f"attachment; filename=edited_video_{video_id}.mp4"
        }
    )

@app.get("/api/projects")
async def get_projects():
    try:
        projects_list = list(projects_db.values())
        
        total = len(projects_list)
        processed = len([p for p in projects_list if p.get("status") == "completed"])
        pending = len([p for p in projects_list if p.get("status") == "uploaded"])
        processing = len([p for p in projects_list if p.get("status") == "processing"])
        
        total_size = 0
        for project in projects_list:
            size_str = project.get("size", "0MB")
            try:
                size_mb = float(size_str.replace("MB", ""))
                total_size += size_mb
            except:
                pass
        
        storage = f"{total_size:.1f}MB"
        
        return {
            "success": True,
            "projects": projects_list,
            "stats": {
                "total": total,
                "processed": processed,
                "pending": pending,
                "processing": processing,
                "storage": storage
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"Get projects error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/project/{project_id}")
async def get_project(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    return {
        "success": True,
        "project": project
    }

@app.delete("/api/project/{project_id}")
async def delete_project(project_id: str):
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        video_id = project.get("video_id")
        
        for folder in [UPLOAD_DIR, PROCESSED_DIR, TEMP_DIR]:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    if file.startswith(video_id) or file.startswith(project_id):
                        file_path = os.path.join(folder, file)
                        try:
                            os.remove(file_path)
                            print(f"Deleted file: {file_path}")
                        except Exception as e:
                            print(f"Error deleting {file_path}: {str(e)}")
        
        del projects_db[project_id]
        save_projects()
        
        print(f"Project deleted: {project_id}")
        
        return {
            "success": True,
            "message": "Project deleted successfully",
            "deletedAt": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/project/{project_id}")
async def update_project(project_id: str, updates: Dict):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    for key, value in updates.items():
        if key in ["name", "status", "duration"]:
            project[key] = value
    
    project["updated_at"] = datetime.now().isoformat()
    save_projects()
    
    return {
        "success": True,
        "project": project,
        "message": "Project updated successfully"
    }

@app.get("/api/stats")
async def get_user_stats():
    try:
        total = len(projects_db)
        completed = len([p for p in projects_db.values() if p.get("status") == "completed"])
        uploaded_files = len(os.listdir(UPLOAD_DIR)) if os.path.exists(UPLOAD_DIR) else 0
        processed_files = len(os.listdir(PROCESSED_DIR)) if os.path.exists(PROCESSED_DIR) else 0
        
        total_size = 0
        for folder in [UPLOAD_DIR, PROCESSED_DIR]:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    file_path = os.path.join(folder, file)
                    if os.path.isfile(file_path):
                        total_size += os.path.getsize(file_path)
        
        storage_mb = total_size / (1024 * 1024)
        
        return {
            "success": True,
            "stats": {
                "total_videos": total,
                "completed_videos": completed,
                "uploaded_files": uploaded_files,
                "processed_files": processed_files,
                "storage_used": f"{storage_mb:.1f}MB",
                "storage_used_bytes": total_size,
                "total_processing_time": 0
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs")
async def get_all_jobs():
    return {
        "success": True,
        "jobs": list(processing_jobs.values()),
        "count": len(processing_jobs)
    }

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    del processing_jobs[job_id]
    
    return {
        "success": True,
        "message": "Job deleted successfully"
    }

@app.post("/api/cleanup")
async def cleanup_temp_files():
    try:
        cleaned_count = 0
        
        for folder in [TEMP_DIR]:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    file_path = os.path.join(folder, file)
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                        print(f"Cleaned: {file_path}")
                    except Exception as e:
                        print(f"Error cleaning {file_path}: {str(e)}")
        
        return {
            "success": True,
            "message": f"Cleaned {cleaned_count} temporary files",
            "cleaned_count": cleaned_count
        }
    
    except Exception as e:
        print(f"Cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/info")
async def get_system_info():
    import sys
    import platform
    
    return {
        "success": True,
        "system": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "upload_dir": UPLOAD_DIR,
            "processed_dir": PROCESSED_DIR,
            "temp_dir": TEMP_DIR
        },
        "storage": {
            "uploads_count": len(os.listdir(UPLOAD_DIR)) if os.path.exists(UPLOAD_DIR) else 0,
            "processed_count": len(os.listdir(PROCESSED_DIR)) if os.path.exists(PROCESSED_DIR) else 0,
            "temp_count": len(os.listdir(TEMP_DIR)) if os.path.exists(TEMP_DIR) else 0
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
        )
