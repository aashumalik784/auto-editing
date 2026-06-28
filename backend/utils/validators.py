# Validators

from config import settings
from utils.logger import logger


class Validators:
    """Input validation"""
    
    @staticmethod
    def validate_video_file(file) -> bool:
        """Validate video file"""
        try:
            # Check content type
            if not file.content_type:
                return False
            
            if not file.content_type.startswith('video/'):
                return False
            
            if file.content_type not in settings.ALLOWED_VIDEO_TYPES:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False
    
    @staticmethod
    def validate_file_size(file) -> bool:
        """Validate file size"""
        try:
            # Read file content to get size
            content = file.file.read()
            file.file.seek(0)  # Reset file pointer
            
            size = len(content)
            
            if size > settings.MAX_FILE_SIZE:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Size validation error: {str(e)}")
            return False
    
    @staticmethod
    def validate_video_id(video_id: str) -> bool:
        """Validate video ID format"""
        try:
            if not video_id:
                return False
            
            # UUID format check
            import uuid
            uuid.UUID(video_id)
            
            return True
            
        except:
            return False
    
    @staticmethod
    def validate_quality(quality: str) -> bool:
        """Validate video quality"""
        valid_qualities = ["1080p", "720p", "480p"]
        return quality in valid_qualities
    
    @staticmethod
    def validate_format(format: str) -> bool:
        """Validate video format"""
        valid_formats = ["mp4", "webm", "mov"]
        return format in valid_formats
