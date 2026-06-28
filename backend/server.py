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

from processors.video_editor import VideoEditor
from processors.audio_processor import AudioProcessor
from processors.caption_generator import CaptionGenerator
from processors.trimmer import VideoTrimmer
from utils.file_handler import FileHandler
from utils.logger import logger
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
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage for processing jobs (in production, use Redis or database)
processing_jobs: Dict[str, Dict] = {}

# Initialize processors
video_editor = VideoEditor()
audio_processor = AudioProcessor()
caption_generator = CaptionGenerator()
video_trimmer = VideoTrimmer()
file_handler = FileHandler()


# Models
class ProcessRequest(BaseModel):
    videoId: str    options: Dict


class ProcessResponse(BaseModel):
    success: bool
    jobId: Optional[str] = None
    message: Optional[str] = None


# Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
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
        file_path = await file_handler.save_upload(video, video_id)
        
        # Create video record
        video_record = {
            "id": video_id,
            "filename": video.filename,
            "path": file_path,
            "size": os.path.getsize(file_path),
            "created_at": datetime.now().isoformat(),
            "status": "uploaded"
        }
        
        logger.info(f"Video uploaded: {video_id}")
        
        return {
            "success": True,
            "videoId": video_id,
            "message": "Video uploaded successfully"        }
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/video/{video_id}")
async def get_video(video_id: str):
    """Get video information"""
    try:
        video_path = f"storage/uploads/{video_id}.mp4"
        
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video not found")
        
        return {
            "success": True,
            "videoUrl": f"/api/video/{video_id}/file",
            "video": {
                "id": video_id,
                "filename": f"{video_id}.mp4"
            }
        }
    
    except Exception as e:
        logger.error(f"Get video error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/video/{video_id}/file")
async def get_video_file(video_id: str):
    """Get video file"""
    video_path = f"storage/uploads/{video_id}.mp4"
    
    if not os.path.exists(video_path):
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
            "status": "processing",
            "progress": 0,
            "message": "Starting processing...",
            "options": options,
            "created_at": datetime.now().isoformat()
        }
        
        # Start processing in background
        background_tasks.add_task(process_video_task, job_id, video_id, options)
        
        logger.info(f"Processing started: {job_id}")
        
        return {
            "success": True,
            "jobId": job_id,
            "message": "Processing started"
        }
    
    except Exception as e:
        logger.error(f"Process error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_video_task(job_id: str, video_id: str, options: Dict):
    """Background task for video processing"""
    try:
        input_path = f"storage/uploads/{video_id}.mp4"
        output_path = f"storage/processed/{video_id}_edited.mp4"
        
        # Update progress
        processing_jobs[job_id]["progress"] = 10
        processing_jobs[job_id]["message"] = "Analyzing video..."
        
        current_path = input_path
        
        # Step 1: Auto-trim silence
        if options.get("autoTrim"):
            processing_jobs[job_id]["progress"] = 20
            processing_jobs[job_id]["message"] = "Removing silent parts..."
            trimmed_path = f"storage/temp/{video_id}_trimmed.mp4"
            await video_trimmer.trim_silence(current_path, trimmed_path)
            current_path = trimmed_path
        
        # Step 2: Generate captions
        if options.get("autoCaptions"):            processing_jobs[job_id]["progress"] = 40
            processing_jobs[job_id]["message"] = "Generating captions..."
            captions = await caption_generator.generate(current_path)
            
            processing_jobs[job_id]["progress"] = 50
            processing_jobs[job_id]["message"] = "Adding captions to video..."
            captioned_path = f"storage/temp/{video_id}_captioned.mp4"
            await video_editor.add_captions(current_path, captions, captioned_path)
            current_path = captioned_path
        
        # Step 3: Add background music
        if options.get("autoMusic") and options.get("musicType") != "none":
            processing_jobs[job_id]["progress"] = 70
            processing_jobs[job_id]["message"] = "Adding background music..."
            music_path = f"assets/music/{options.get('musicType')}.mp3"
            music_volume = options.get("musicVolume", 20) / 100
            mixed_path = f"storage/temp/{video_id}_mixed.mp4"
            await audio_processor.add_background_music(current_path, music_path, mixed_path, music_volume)
            current_path = mixed_path
        
        # Step 4: Color correction
        if options.get("autoColor"):
            processing_jobs[job_id]["progress"] = 85
            processing_jobs[job_id]["message"] = "Applying color correction..."
            colored_path = f"storage/temp/{video_id}_colored.mp4"
            await video_editor.apply_color_correction(current_path, colored_path)
            current_path = colored_path
        
        # Step 5: Final export
        processing_jobs[job_id]["progress"] = 95
        processing_jobs[job_id]["message"] = "Finalizing video..."
        
        quality = options.get("quality", "1080p")
        format_type = options.get("format", "mp4")
        
        await video_editor.export_video(current_path, output_path, quality, format_type)
        
        # Update job status
        processing_jobs[job_id]["status"] = "completed"
        processing_jobs[job_id]["progress"] = 100
        processing_jobs[job_id]["message"] = "Processing completed"
        processing_jobs[job_id]["output_path"] = output_path
        
        logger.info(f"Processing completed: {job_id}")
        
        # Clean up temp files
        file_handler.cleanup_temp_files(video_id)
    
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")        processing_jobs[job_id]["status"] = "failed"
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
        output_path = f"storage/processed/{video_id}_edited.mp4"
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=404, detail="Processed video not found")
        
        return {
            "success": True,
            "downloadUrl": f"/api/download/{video_id}",
            "format": "mp4"
        }
    
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{video_id}")
async def download_video(video_id: str):
    """Download processed video"""
    output_path = f"storage/processed/{video_id}_edited.mp4"
    
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        output_path,        media_type="video/mp4",
        filename=f"edited_video_{video_id}.mp4"
    )


@app.get("/api/projects")
async def get_projects():
    """Get all projects"""
    # In production, fetch from database
    return {
        "success": True,
        "projects": [],
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
        # Delete from storage
        file_handler.delete_video(project_id)
        
        logger.info(f"Project deleted: {project_id}")
        
        return {
            "success": True,
            "message": "Project deleted successfully"
        }
    
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_user_stats():
    """Get user statistics"""
    # In production, calculate from database
    return {
        "success": True,
        "stats": {
            "total_videos": 0,
            "total_processing_time": 0,
            "storage_used": 0        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
