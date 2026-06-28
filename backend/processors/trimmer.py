# Video Trimmer

from moviepy.editor import VideoFileClip
import numpy as np
from utils.logger import logger


class VideoTrimmer:
    """Trim silent parts from video"""
    
    def __init__(self):
        self.logger = logger
    
    async def trim_silence(self, input_path: str, output_path: str, silence_threshold: float = 0.03, chunk_size: int = 10):
        """Remove silent parts from video"""
        try:
            self.logger.info(f"Trimming silence from: {input_path}")
            
            # Load video
            video = VideoFileClip(input_path)
            
            # Find non-silent segments
            non_silent_segments = self._find_non_silent_segments(
                video, silence_threshold, chunk_size
            )
            
            if not non_silent_segments:
                self.logger.warning("No non-silent segments found")
                # Just copy the video
                video.write_videofile(output_path)
                return
            
            # Concatenate non-silent segments
            clips = []
            for start, end in non_silent_segments:
                clips.append(video.subclip(start, end))
            
            # Concatenate all clips
            from moviepy.editor import concatenate_videoclips
            final_video = concatenate_videoclips(clips)
            
            # Write output
            final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            self.logger.info(f"Silence trimmed: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error trimming silence: {str(e)}")
            raise
        def _find_non_silent_segments(self, video, threshold: float, chunk_size: int):
        """Find segments that are not silent"""
        segments = []
        
        # Get audio data
        audio = video.audio
        duration = video.duration
        
        current_time = 0
        segment_start = None
        
        while current_time < duration:
            # Get audio chunk
            end_time = min(current_time + chunk_size, duration)
            
            # Calculate average volume
            audio_chunk = audio.subclip(current_time, end_time)
            
            # Simple volume check (you can improve this)
            try:
                # This is a simplified check
                # In production, use proper audio analysis
                has_sound = True  # Placeholder
                
                if has_sound:
                    if segment_start is None:
                        segment_start = current_time
                else:
                    if segment_start is not None:
                        segments.append((segment_start, current_time))
                        segment_start = None
                
            except Exception as e:
                self.logger.warning(f"Error analyzing chunk at {current_time}: {str(e)}")
            
            current_time = end_time
        
        # Add last segment
        if segment_start is not None:
            segments.append((segment_start, duration))
        
        return segments
    
    async def trim_to_duration(self, input_path: str, output_path: str, max_duration: float):
        """Trim video to specific duration"""
        try:
            video = VideoFileClip(input_path)
            
            if video.duration > max_duration:
                video = video.subclip(0, max_duration)            
            video.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            self.logger.info(f"Video trimmed to {max_duration}s: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error trimming to duration: {str(e)}")
            raise
