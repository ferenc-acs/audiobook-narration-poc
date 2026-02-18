# Audiobook Narration PoC

A lightweight proof-of-concept for emotional audiobook narration using Piper TTS. Emotion is controlled via Piper's native synthesis parameters—no SSML required.

## Features

- 🎭 **5 Emotions**: neutral, suspense, action, anger, fearful
- 🔧 **Native Piper Parameters**: Uses `length_scale`, `noise_scale`, `noise_w` for emotional control
- ⏸️ **Post-Generation Pauses**: pydub-based silence injection (SSML-free)
- 📢 **Loudness Normalization**: ffmpeg-based LUFS normalization (-16 LUFS target)
- 🎯 **Simple JSON Input**: Easy-to-edit narration scripts

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ferenc-acs/audiobook-narration-poc.git
cd audiobook-narration-poc

# Install dependencies
pip install -r requirements.txt

# Download a Piper voice model
# Example: https://github.com/rhasspy/piper/releases
# Download .onnx and .json files to a models/ directory
```

### Usage

```bash
python narrator_cli.py examples/ghost_story.json \
    --model path/to/voice.onnx \
    --output story.mp3
```

### Input Format

Create a JSON file with narration segments:

```json
{
  "title": "My Story",
  "segments": [
    {
      "text": "It was a dark and stormy night.",
      "emotion": "suspense",
      "pause_after": "long"
    },
    {
      "text": "Suddenly, a shot rang out!",
      "emotion": "action",
      "pause_after": "short"
    }
  ]
}
```

**Emotions**: `neutral`, `suspense`, `action`, `anger`, `fearful`  
**Pauses**: `short` (250ms), `medium` (500ms), `long` (1000ms), `very_long` (2000ms)

## Architecture

```
Input JSON → Parser → Emotion Mapper → Generator → Post-Processor → Output
                ↓           ↓              ↓            ↓
            Utterances   Config      Raw Audio    Mixed Audio
```

| Module | Purpose |
|--------|---------|
| `input_parser.py` | Parse JSON input with text + emotion tags |
| `emotion_config.py` | Map emotion names to Piper parameters |
| `piper_wrapper.py` | Generate audio using piper-tts |
| `post_processor.py` | Concatenate segments + inject pauses |

## Configuration

Edit `config/emotions.json` to customize emotion parameters:

```json
{
  "emotions": {
    "suspense": {
      "length_scale": 1.2,
      "noise_scale": 0.667,
      "noise_w": 0.8
    }
  }
}
```

## Example

Generate the sample ghost story:

```bash
python narrator_cli.py examples/ghost_story.json \
    --model models/en_US-amy-medium.onnx \
    --output the_old_lighthouse.mp3
```

## Requirements

- Python 3.8+
- Piper voice model (.onnx file)
- ffmpeg (for normalization)

## License

MIT
