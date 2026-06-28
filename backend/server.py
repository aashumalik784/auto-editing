# FastAPI Backend Server

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
import os
import shutil
from datetime import datetime

from config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Auto-Editing API",
    description="AI-powered video editing API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage for processing jobs (in production, use Redis or database)
processing_jobs: Dict[str, Dict] = {}


# Models
class ProcessRequest(BaseModel):
    videoId: str
    options: Dict


class ProcessResponse(BaseModel):
    success: bool
    jobId: Optional[str] = None
    message: Optional[str] = None


# Routes
@app.get("/")
async def root():
    """Health check endpoint"""    return {
        "status": "healthy",
        "service": "Auto-Editing API",
        "version": "1.0.0"
    }


@app.post("/api/upload")
async def upload_video(background_tasks: BackgroundTasks, video: UploadFile = File(...)):
    """Upload a video file"""
    try:
        # Validate file
        if not video.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Generate unique ID
        video_id = str(uuid.uuid4())
        
        # Save file
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_extension = os.path.splitext(video.filename)[1] or '.mp4'
        file_path = os.path.join(settings.UPLOAD_DIR, f"{video_id}{file_extension}")
        
        with open(file_path, 'wb') as buffer:
            content = await video.read()
            buffer.write(content)
        
        print(f"Video uploaded: {video_id} -> {file_path}")
        
        return {
            "success": True,
            "videoId": video_id,
            "message": "Video uploaded successfully"
        }
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/video/{video_id}")
async def get_video(video_id: str):
    """Get video information"""
    try:
        # Find the video file
        video_path = None
        for ext in ['.mp4', '.avi', '.mov', '.mkv']:
            test_path = os.path.join(settings.UPLOAD_DIR, f"{video_id}{ext}")
            if os.path.exists(test_path):
                video_path = test_path                break
        
        if not video_path:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return {
            "success": True,
            "videoUrl": f"/api/video/{video_id}/file",
            "video": {
                "id": video_id,
                "filename": os.path.basename(video_path)
            }
        }
    
    except Exception as e:
        print(f"Get video error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/video/{video_id}/file")
async def get_video_file(video_id: str):
    """Get video file"""
    video_path = None
    for ext in ['.mp4', '.avi', '.mov', '.mkv']:
        test_path = os.path.join(settings.UPLOAD_DIR, f"{video_id}{ext}")
        if os.path.exists(test_path):
            video_path = test_path
            break
    
    if not video_path:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(video_path, media_type="video/mp4")


@app.post("/api/process")
async def process_video(request: ProcessRequest, background_tasks: BackgroundTasks):
    """Process video with AI"""
    try:
        video_id = request.videoId
        options = request.options
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Create job record
        processing_jobs[job_id] = {
            "id": job_id,
            "video_id": video_id,
            "status": "processing",            "progress": 0,
            "message": "Starting processing...",
            "options": options,
            "created_at": datetime.now().isoformat()
        }
        
        # Start processing in background
        background_tasks.add_task(process_video_task, job_id, video_id, options)
        
        print(f"Processing started: {job_id}")
        
        return {
            "success": True,
            "jobId": job_id,
            "message": "Processing started"
        }
    
    except Exception as e:
        print(f"Process error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_video_task(job_id: str, video_id: str, options: Dict):
    """Background task for video processing"""
    try:
        # Find input file
        input_path = None
        for ext in ['.mp4', '.avi', '.mov', '.mkv']:
            test_path = os.path.join(settings.UPLOAD_DIR, f"{video_id}{ext}")
            if os.path.exists(test_path):
                input_path = test_path
                break
        
        if not input_path:
            raise Exception("Input video not found")
        
        output_path = os.path.join(settings.PROCESSED_DIR, f"{video_id}_edited.mp4")
        os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
        os.makedirs(settings.TEMP_DIR, exist_ok=True)
        
        # Update progress
        processing_jobs[job_id]["progress"] = 10
        processing_jobs[job_id]["message"] = "Analyzing video..."
        
        current_path = input_path
        
        # Step 1: Auto-trim silence (simplified)
        if options.get("autoTrim"):
            processing_jobs[job_id]["progress"] = 30
            processing_jobs[job_id]["message"] = "Removing silent parts..."            # For now, just copy the file
            trimmed_path = os.path.join(settings.TEMP_DIR, f"{video_id}_trimmed.mp4")
            shutil.copy(current_path, trimmed_path)
            current_path = trimmed_path
        
        # Step 2: Captions (placeholder)
        if options.get("autoCaptions"):
            processing_jobs[job_id]["progress"] = 50
            processing_jobs[job_id]["message"] = "Generating captions..."
            # Placeholder - will add Whisper later
        
        # Step 3: Background music (placeholder)
        if options.get("autoMusic") and options.get("musicType") != "none":
            processing_jobs[job_id]["progress"] = 70
            processing_jobs[job_id]["message"] = "Adding background music..."
            # Placeholder
        
        # Step 4: Color correction (placeholder)
        if options.get("autoColor"):
            processing_jobs[job_id]["progress"] = 85
            processing_jobs[job_id]["message"] = "Applying color correction..."
            # Placeholder
        
        # Step 5: Final export
        processing_jobs[job_id]["progress"] = 95
        processing_jobs[job_id]["message"] = "Finalizing video..."
        
        # Copy to output (in real implementation, use FFmpeg)
        shutil.copy(current_path, output_path)
        
        # Update job status
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
    """Get processing status"""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
        job = processing_jobs[job_id]
    
    return {
        "success": True,
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"]
    }


@app.post("/api/export/{video_id}")
async def export_video(video_id: str):
    """Export processed video"""
    try:
        output_path = os.path.join(settings.PROCESSED_DIR, f"{video_id}_edited.mp4")
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=404, detail="Processed video not found")
        
        return {
            "success": True,
            "downloadUrl": f"/api/download/{video_id}",
            "format": "mp4"
        }
    
    except Exception as e:
        print(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{video_id}")
async def download_video(video_id: str):
    """Download processed video"""
    output_path = os.path.join(settings.PROCESSED_DIR, f"{video_id}_edited.mp4")
    
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"edited_video_{video_id}.mp4"
    )


@app.get("/api/projects")
async def get_projects():
    """Get all projects"""
    return {
        "success": True,        "projects": [],
        "stats": {
            "total": 0,
            "processed": 0,
            "pending": 0,
            "storage": "0 MB"
        }
    }


@app.delete("/api/project/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        # Delete files
        for folder in [settings.UPLOAD_DIR, settings.PROCESSED_DIR]:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    if file.startswith(project_id):
                        os.remove(os.path.join(folder, file))
        
        print(f"Project deleted: {project_id}")
        
        return {
            "success": True,
            "message": "Project deleted successfully"
        }
    
    except Exception as e:
        print(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_user_stats():
    """Get user statistics"""
    return {
        "success": True,
        "stats": {
            "total_videos": 0,
            "total_processing_time": 0,
            "storage_used": 0
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
