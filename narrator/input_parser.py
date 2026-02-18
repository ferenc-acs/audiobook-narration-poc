"""Parse JSON input with text and emotion tags."""

import json
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Segment:
    """A single narration segment with emotion and pause info."""
    text: str
    emotion: str = "neutral"
    pause_after: str = "medium"


class InputParser:
    """Parse narration input JSON into segments."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize parser with optional config path."""
        self.config_path = config_path
    
    def parse(self, input_data: dict) -> List[Segment]:
        """Parse JSON dict into list of Segments.
        
        Args:
            input_data: JSON dict with 'segments' array
            
        Returns:
            List of Segment objects
        """
        segments = []
        raw_segments = input_data.get("segments", [])
        
        for seg in raw_segments:
            segment = Segment(
                text=seg.get("text", ""),
                emotion=seg.get("emotion", "neutral"),
                pause_after=seg.get("pause_after", "medium")
            )
            segments.append(segment)
        
        return segments
    
    def parse_file(self, filepath: str) -> List[Segment]:
        """Parse JSON file into list of Segments.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            List of Segment objects
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return self.parse(data)
