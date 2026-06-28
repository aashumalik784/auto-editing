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
        
        # Save to database (implement this)
        # db.save_video(video_record)
        
        logger.info(f"Video uploaded: {video_id}")
        
        return {            "success": True,
            "videoId": video_id,
            "message": "Video uploaded successfully"
        }
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/video/{video_id}")
async def get_video(video_id: str):
    """Get video information"""
    try:
        # Get video from database (implement this)
        # video = db.get_video(video_id)
        
        # For now, return mock data
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
async def process_video(request: ProcessRequest, background_tasks: BackgroundTasks):    """Process video with AI"""
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
        
        # Step 1: Auto-trim silence
        if options.get("autoTrim"):
            processing_jobs[job_id]["progress"] = 20
            processing_jobs[job_id]["message"] = "Removing silent parts..."
            input_path = await video_trimmer.trim_silence(input_path, f"storage/temp/{video_id}_trimmed.mp4")        
        # Step 2: Generate captions
        if options.get("autoCaptions"):
            processing_jobs[job_id]["progress"] = 40
            processing_jobs[job_id]["message"] = "Generating captions..."
            captions = await caption_generator.generate(input_path)
            
            processing_jobs[job_id]["progress"] = 50
            processing_jobs[job_id]["message"] = "Adding captions to video..."
            input_path = await video_editor.add_captions(input_path, captions, f"storage/temp/{video_id}_captioned.mp4")
        
        # Step 3: Add background music
        if options.get("autoMusic") and options.get("musicType") != "none":
            processing_jobs[job_id]["progress"] = 70
            processing_jobs
