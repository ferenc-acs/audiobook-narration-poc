"""Post-processor for concatenating audio and injecting silences."""

import io
import subprocess
import tempfile
from pathlib import Path
from typing import List

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class PostProcessor:
    """Concatenate audio segments and inject pauses."""
    
    def __init__(self):
        """Initialize post-processor."""
        if not PYDUB_AVAILABLE:
            raise RuntimeError(
                "pydub not installed. Install with: pip install pydub"
            )
    
    def concatenate_segments(
        self,
        audio_segments: List[bytes],
        pause_ms: List[int]
    ) -> AudioSegment:
        """Concatenate audio segments with pauses.
        
        Args:
            audio_segments: List of raw WAV audio bytes
            pause_ms: List of pause durations after each segment
            
        Returns:
            Combined AudioSegment
        """
        if not audio_segments:
            return AudioSegment.empty()
        
        combined = AudioSegment.empty()
        
        for i, segment_bytes in enumerate(audio_segments):
            # Load segment
            segment = AudioSegment.from_wav(io.BytesIO(segment_bytes))
            
            # Add segment to output
            combined += segment
            
            # Add pause (except after last segment)
            if i < len(audio_segments) - 1:
                pause_duration = pause_ms[i] if i < len(pause_ms) else 500
                silence = AudioSegment.silent(duration=pause_duration)
                combined += silence
        
        return combined
    
    def normalize_audio(
        self,
        audio: AudioSegment,
        target_lufs: float = -16.0,
        true_peak: float = -1.5,
        lra: float = 11.0
    ) -> bytes:
        """Normalize audio using ffmpeg loudnorm filter.
        
        Args:
            audio: Input AudioSegment
            target_lufs: Target loudness in LUFS (default -16)
            true_peak: True peak limit in dB (default -1.5)
            lra: Loudness range in LU (default 11)
            
        Returns:
            Normalized audio as WAV bytes
        """
        # Export to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_in:
            audio.export(temp_in.name, format='wav')
            temp_in_path = temp_in.name
        
        try:
            # Run ffmpeg with loudnorm
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output
                '-i', temp_in_path,
                '-af', f'loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}',
                '-ar', '22050',  # Sample rate
                '-ac', '1',  # Mono
                '-f', 'wav',
                'pipe:1'  # Output to stdout
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                check=True
            )
            
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ffmpeg normalization failed: {e.stderr.decode()}")
        finally:
            Path(temp_in_path).unlink(missing_ok=True)
    
    def export_to_file(
        self,
        audio: AudioSegment,
        output_path: str,
        format: str = "mp3",
        normalize: bool = True
    ):
        """Export audio to file with optional normalization.
        
        Args:
            audio: AudioSegment to export
            output_path: Output file path
            format: Output format (mp3, wav, ogg)
            normalize: Whether to apply loudness normalization
        """
        if normalize and format == 'wav':
            # Use ffmpeg normalization for WAV
            normalized_bytes = self.normalize_audio(audio)
            with open(output_path, 'wb') as f:
                f.write(normalized_bytes)
        else:
            # Use pydub export (normalization optional)
            if normalize:
                # Export to temp, normalize, then convert
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_in:
                    audio.export(temp_in.name, format='wav')
                    temp_in_path = temp_in.name
                
                try:
                    cmd = [
                        'ffmpeg',
                        '-y',
                        '-i', temp_in_path,
                        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                        output_path
                    ]
                    subprocess.run(cmd, capture_output=True, check=True)
                finally:
                    Path(temp_in_path).unlink(missing_ok=True)
            else:
                audio.export(output_path, format=format)
