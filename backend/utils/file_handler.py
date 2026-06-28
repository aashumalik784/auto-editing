# File Handler

import os
import shutil
from fastapi import UploadFile
from config import settings
from utils.logger import logger


class FileHandler:
    """Handle file operations"""
    
    def __init__(self):
        self.logger = logger
    
    async def save_upload(self, file: UploadFile, video_id: str) -> str:
        """Save uploaded file"""
        try:
            # Create upload directory if not exists
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            
            # Generate file path
            file_extension = os.path.splitext(file.filename)[1] or '.mp4'
            file_path = os.path.join(settings.UPLOAD_DIR, f"{video_id}{file_extension}")
            
            # Save file
            with open(file_path, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            self.logger.info(f"File saved: {file_path}")
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error saving upload: {str(e)}")
            raise
    
    def delete_video(self, video_id: str):
        """Delete video and related files"""
        try:
            # Delete from uploads
            upload_pattern = os.path.join(settings.UPLOAD_DIR, f"{video_id}.*")
            for file in os.listdir(settings.UPLOAD_DIR):
                if file.startswith(video_id):
                    os.remove(os.path.join(settings.UPLOAD_DIR, file))
            
            # Delete from processed
            processed_pattern = os.path.join(settings.PROCESSED_DIR, f"{video_id}*")
            for file in os.listdir(settings.PROCESSED_DIR):
                if file.startswith(video_id):
                    os.remove(os.path.join(settings.PROCESSED_DIR, file))
            
            self.logger.info(f"Video deleted: {video_id}")
            
        except Exception as e:
            self.logger.error(f"Error deleting video: {str(e)}")
            raise
    
    def cleanup_temp_files(self, video_id: str):
        """Clean up temporary files"""
        try:
            temp_dir = settings.TEMP_DIR
            
            for file in os.listdir(temp_dir):
                if file.startswith(video_id):
                    file_path = os.path.join(temp_dir, file)
                    os.remove(file_path)
            
            self.logger.info(f"Temp files cleaned: {video_id}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning temp files: {str(e)}")
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except:
            return 0
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size to human readable"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ("B", "KB", "MB", "GB", "TB")
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
