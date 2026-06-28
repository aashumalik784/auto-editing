# Audio Processor

from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
from utils.logger import logger


class AudioProcessor:
    """Audio processing operations"""
    
    def __init__(self):
        self.logger = logger
    
    async def add_background_music(self, video_path: str, music_path: str, output_path: str, music_volume: float = 0.2):
        """Add background music to video"""
        try:
            # Load video
            video = VideoFileClip(video_path)
            
            # Load background music
            music = AudioFileClip(music_path)
            
            # Loop music if it's shorter than video
            if music.duration < video.duration:
                music = music.loop(duration=video.duration)
            else:
                music = music.subclip(0, video.duration)
            
            # Adjust music volume
            music = music.volumex(music_volume)
            
            # Composite audio
            if video.audio:
                final_audio = CompositeAudioClip([video.audio, music])
            else:
                final_audio = music
            
            # Set audio to video
            final_video = video.set_audio(final_audio)
            
            # Write output
            final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            self.logger.info(f"Background music added: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error adding background music: {str(e)}")
            raise
    
    async def normalize_audio(self, input_path: str, output_path: str):
        """Normalize audio levels"""
        try:
            # Use FFmpeg for audio normalization
            command = [
                'ffmpeg',
                '-i', input_path,
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                '-c:v', 'copy',
                '-y',
                output_path
            ]
            
            subprocess.run(command, check=True, capture_output=True)
            
            self.logger.info(f"Audio normalized: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error normalizing audio: {str(e)}")
            raise
    
    async def remove_noise(self, input_path: str, output_path: str):
        """Remove background noise from audio"""
        try:
            # Use FFmpeg for noise reduction
            command = [
                'ffmpeg',
                '-i', input_path,
                '-af', 'afftdn=nf=-25',
                '-c:v', 'copy',
                '-y',
                output_path
            ]
            
            subprocess.run(command, check=True, capture_output=True)
            
            self.logger.info(f"Noise removed: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error removing noise: {str(e)}")
            raise
