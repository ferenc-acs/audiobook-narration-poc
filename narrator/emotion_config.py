"""Load emotion to Piper parameter mappings."""

import json
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class EmotionConfig:
    """Piper synthesis parameters for an emotion."""
    length_scale: float
    noise_scale: float
    noise_w: float
    description: str = ""


class EmotionMapper:
    """Map emotion names to Piper SynthesisConfig parameters."""
    
    DEFAULT_EMOTION = EmotionConfig(
        length_scale=1.0,
        noise_scale=0.5,
        noise_w=0.6,
        description="Default neutral narration"
    )
    
    def __init__(self, config_path: str = "config/emotions.json"):
        """Initialize mapper with config file.
        
        Args:
            config_path: Path to emotions JSON config
        """
        self.config_path = config_path
        self.emotions: Dict[str, EmotionConfig] = {}
        self.pauses: Dict[str, int] = {}
        self._load_config()
    
    def _load_config(self):
        """Load emotion mappings from config file."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Load emotions
        for name, params in data.get("emotions", {}).items():
            self.emotions[name] = EmotionConfig(
                length_scale=params.get("length_scale", 1.0),
                noise_scale=params.get("noise_scale", 0.5),
                noise_w=params.get("noise_w", 0.6),
                description=params.get("description", "")
            )
        
        # Load pauses
        self.pauses = data.get("pauses", {
            "short": 250,
            "medium": 500,
            "long": 1000,
            "very_long": 2000
        })
    
    def get_config(self, emotion: str) -> EmotionConfig:
        """Get Piper config for an emotion.
        
        Args:
            emotion: Emotion name
            
        Returns:
            EmotionConfig with Piper parameters
        """
        return self.emotions.get(emotion, self.DEFAULT_EMOTION)
    
    def get_pause_ms(self, pause_type: str) -> int:
        """Get pause duration in milliseconds.
        
        Args:
            pause_type: Pause type (short, medium, long, very_long)
            
        Returns:
            Pause duration in ms
        """
        return self.pauses.get(pause_type, 500)
    
    def list_emotions(self) -> list:
        """Return list of available emotion names."""
        return list(self.emotions.keys())
