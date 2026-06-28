# Caption Generator using Whisper AI

import whisper
from utils.logger import logger


class CaptionGenerator:
    """Generate captions using Whisper AI"""
    
    def __init__(self, model_name: str = "base"):
        self.logger = logger
        self.model_name = model_name
        self.model = None
    
    def _load_model(self):
        """Load Whisper model"""
        if self.model is None:
            self.logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
    
    async def generate(self, video_path: str, language: str = "en"):
        """Generate captions from video"""
        try:
            # Load model
            self._load_model()
            
            self.logger.info(f"Generating captions for: {video_path}")
            
            # Transcribe audio
            result = self.model.transcribe(
                video_path,
                language=language,
                task="transcribe",
                verbose=False
            )
            
            # Format captions
            captions = []
            for segment in result.get('segments', []):
                captions.append({
                    'start': segment.get('start', 0),
                    'end': segment.get('end', 0),
                    'text': segment.get('text', '').strip()
                })
            
            self.logger.info(f"Generated {len(captions)} captions")
            
            return captions
            
        except Exception as e:
            self.logger.error(f"Error generating captions: {str(e)}")
            raise
    
    async def generate_srt(self, video_path: str, output_path: str, language: str = "en"):
        """Generate SRT subtitle file"""
        try:
            captions = await self.generate(video_path, language)
            
            # Write SRT file
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, caption in enumerate(captions, 1):
                    start_time = self._format_srt_time(caption['start'])
                    end_time = self._format_srt_time(caption['end'])
                    text = caption['text']
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
            
            self.logger.info(f"SRT file generated: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error generating SRT: {str(e)}")
            raise
    
    def _format_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
