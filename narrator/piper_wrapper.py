"""Piper TTS wrapper for generating audio with emotion."""

import io
import wave
from pathlib import Path
from typing import Optional, Union

try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False

from .emotion_config import EmotionConfig


class PiperWrapper:
    """Wrapper around piper-tts for emotional narration."""
    
    def __init__(self, model_path: str):
        """Initialize Piper voice model.
        
        Args:
            model_path: Path to Piper .onnx model file
        """
        if not PIPER_AVAILABLE:
            raise RuntimeError(
                "piper-tts package not installed. "
                "Install with: pip install piper-tts"
            )
        
        self.model_path = model_path
        self.voice = None
        self._load_voice()
    
    def _load_voice(self):
        """Load the Piper voice model."""
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Piper model not found: {self.model_path}")
        
        self.voice = PiperVoice.load(self.model_path)
    
    def synthesize(
        self,
        text: str,
        config: Optional[EmotionConfig] = None
    ) -> bytes:
        """Synthesize audio with emotion config.
        
        Args:
            text: Text to synthesize
            config: Emotion config (uses default if None)
            
        Returns:
            Raw WAV audio bytes
        """
        if config is None:
            config = EmotionConfig(
                length_scale=1.0,
                noise_scale=0.5,
                noise_w=0.6
            )
        
        # Create synthesis config
        synthesis_config = self.voice.config
        
        # Set emotion parameters via native SynthesisConfig
        # Piper uses these parameters directly, no SSML needed
        if hasattr(synthesis_config, 'length_scale'):
            synthesis_config.length_scale = config.length_scale
        if hasattr(synthesis_config, 'noise_scale'):
            synthesis_config.noise_scale = config.noise_scale
        if hasattr(synthesis_config, 'noise_w'):
            synthesis_config.noise_w = config.noise_w
        
        # Synthesize to bytes buffer
        audio_buffer = io.BytesIO()
        
        with wave.open(audio_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(22050)  # 22.05kHz
            
            # Generate audio
            for audio_bytes in self.voice.synthesize_stream_raw(
                text,
                length_scale=config.length_scale,
                noise_scale=config.noise_scale,
                noise_w=config.noise_w
            ):
                wav_file.writeframes(audio_bytes)
        
        return audio_buffer.getvalue()
    
    def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        config: Optional[EmotionConfig] = None
    ):
        """Synthesize and save to WAV file.
        
        Args:
            text: Text to synthesize
            output_path: Output WAV file path
            config: Emotion config
        """
        audio_bytes = self.synthesize(text, config)
        with open(output_path, 'wb') as f:
            f.write(audio_bytes)
