"""Tests for audiobook narrator."""

import json
import tempfile
from pathlib import Path

from narrator.input_parser import InputParser, Segment
from narrator.emotion_config import EmotionMapper, EmotionConfig


def test_parse_segment():
    """Test parsing a single segment."""
    parser = InputParser()
    data = {
        "segments": [
            {"text": "Hello world", "emotion": "neutral", "pause_after": "short"}
        ]
    }
    
    segments = parser.parse(data)
    
    assert len(segments) == 1
    assert segments[0].text == "Hello world"
    assert segments[0].emotion == "neutral"
    assert segments[0].pause_after == "short"


def test_parse_multiple_segments():
    """Test parsing multiple segments."""
    parser = InputParser()
    data = {
        "segments": [
            {"text": "First", "emotion": "neutral"},
            {"text": "Second", "emotion": "suspense"},
            {"text": "Third", "emotion": "action"}
        ]
    }
    
    segments = parser.parse(data)
    
    assert len(segments) == 3
    assert segments[1].emotion == "suspense"
    assert segments[2].emotion == "action"


def test_default_values():
    """Test default emotion and pause values."""
    parser = InputParser()
    data = {
        "segments": [{"text": "Test"}]
    }
    
    segments = parser.parse(data)
    
    assert segments[0].emotion == "neutral"
    assert segments[0].pause_after == "medium"


def test_parse_file():
    """Test parsing from file."""
    parser = InputParser()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"segments": [{"text": "From file"}]}, f)
        temp_path = f.name
    
    try:
        segments = parser.parse_file(temp_path)
        assert len(segments) == 1
        assert segments[0].text == "From file"
    finally:
        Path(temp_path).unlink()


def test_emotion_mapper_loads_config():
    """Test emotion mapper loads config correctly."""
    # Create temp config
    config = {
        "emotions": {
            "test_emotion": {
                "length_scale": 1.5,
                "noise_scale": 0.3,
                "noise_w": 0.4,
                "description": "Test"
            }
        },
        "pauses": {
            "test_pause": 999
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name
    
    try:
        mapper = EmotionMapper(temp_path)
        
        emotion = mapper.get_config("test_emotion")
        assert emotion.length_scale == 1.5
        assert emotion.noise_scale == 0.3
        assert emotion.noise_w == 0.4
        
        pause = mapper.get_pause_ms("test_pause")
        assert pause == 999
    finally:
        Path(temp_path).unlink()


def test_emotion_mapper_defaults():
    """Test emotion mapper returns defaults for unknown emotions."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"emotions": {}, "pauses": {}}, f)
        temp_path = f.name
    
    try:
        mapper = EmotionMapper(temp_path)
        
        # Unknown emotion should return default
        emotion = mapper.get_config("unknown")
        assert emotion.length_scale == 1.0
        assert emotion.noise_scale == 0.5
        assert emotion.noise_w == 0.6
        
        # Unknown pause should return default (500ms)
        pause = mapper.get_pause_ms("unknown")
        assert pause == 500
    finally:
        Path(temp_path).unlink()


def test_segment_dataclass():
    """Test Segment dataclass creation."""
    segment = Segment(text="Hello", emotion="suspense", pause_after="long")
    
    assert segment.text == "Hello"
    assert segment.emotion == "suspense"
    assert segment.pause_after == "long"


def test_emotion_config_dataclass():
    """Test EmotionConfig dataclass creation."""
    config = EmotionConfig(
        length_scale=1.2,
        noise_scale=0.6,
        noise_w=0.7,
        description="Test emotion"
    )
    
    assert config.length_scale == 1.2
    assert config.noise_scale == 0.6
    assert config.noise_w == 0.7
    assert config.description == "Test emotion"


if __name__ == '__main__':
    # Run tests
    import sys
    
    tests = [
        test_parse_segment,
        test_parse_multiple_segments,
        test_default_values,
        test_parse_file,
        test_emotion_mapper_loads_config,
        test_emotion_mapper_defaults,
        test_segment_dataclass,
        test_emotion_config_dataclass,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test.__name__}: {e}")
            failed += 1
    
    print()
    if failed == 0:
        print("All tests passed!")
        sys.exit(0)
    else:
        print(f"{failed} test(s) failed")
        sys.exit(1)
