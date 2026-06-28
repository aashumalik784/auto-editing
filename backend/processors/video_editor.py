# Video Editor Processor

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
import subprocess
from utils.logger import logger


class VideoEditor:
    """Video editing operations"""
    
    def __init__(self):
        self.logger = logger
    
    async def add_captions(self, input_path: str, captions: list, output_path: str):
        """Add captions to video"""
        try:
            video = VideoFileClip(input_path)
            
            # Create caption clips
            caption_clips = []
            
            for caption in captions:
                start_time = caption.get('start', 0)
                end_time = caption.get('end', 0)
                text = caption.get('text', '')
                
                # Create text clip
                txt_clip = (TextClip(text, fontsize=40, color='white', font='Arial-Bold',
                                    stroke_color='black', stroke_width=2)
                           .set_position(('center', 'bottom'))
                           .set_start(start_time)
                           .set_end(end_time))
                
                caption_clips.append(txt_clip)
            
            # Composite video with captions
            final_video = CompositeVideoClip([video] + caption_clips)
            
            # Write output
            final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            self.logger.info(f"Captions added: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error adding captions: {str(e)}")
            raise
    
    async def apply_color_correction(self, input_path: str, output_path: str):
        """Apply automatic color correction"""
        try:            # Use FFmpeg for color correction
            command = [
                'ffmpeg',
                '-i', input_path,
                '-vf', 'eq=brightness=0.06:contrast=1.2:saturation=1.3',
                '-c:a', 'copy',
                '-y',
                output_path
            ]
            
            subprocess.run(command, check=True, capture_output=True)
            
            self.logger.info(f"Color correction applied: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error applying color correction: {str(e)}")
            raise
    
    async def export_video(self, input_path: str, output_path: str, quality: str = "1080p", format: str = "mp4"):
        """Export video with specified quality"""
        try:
            # Map quality to resolution
            quality_map = {
                "1080p": "1920:1080",
                "720p": "1280:720",
                "480p": "854:480"
            }
            
            resolution = quality_map.get(quality, "1920:1080")
            
            # Use FFmpeg for export
            command = [
                'ffmpeg',
                '-i', input_path,
                '-vf', f'scale={resolution}',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-y',
                output_path
            ]
            
            subprocess.run(command, check=True, capture_output=True)
            
            self.logger.info(f"Video exported: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting video: {str(e)}")            raise
