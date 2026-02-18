# Audiobook Narration POC - Architecture

> **Principle:** Real engineering over checkbox requirements. No SSML—Piper's native parameters do emotion better.

---

## Overview

A lightweight pipeline that transforms marked-up text into emotionally-narrated audio using Piper TTS. Emotion is controlled via Piper's native synthesis parameters, not SSML.

---

## 5-Module Architecture

### 1. Parser (`parser.py`)
**Input:** JSON with text + emotion tags  
**Output:** List of utterances with emotion metadata

```json
{
  "segments": [
    {"text": "The door creaked open.", "emotion": "suspense", "pause_after": "long"},
    {"text": "He ran.", "emotion": "action", "pause_after": "short"}
  ]
}
```

**Responsibilities:**
- Parse input JSON
- Extract text + emotion tags
- Parse `[pause=X]` markers
- Validate emotion names against mapper

---

### 2. Emotion Mapper (`emotion_mapper.py`)
**Input:** Emotion name  
**Output:** Piper `SynthesisConfig` parameters

| Emotion  | length_scale | noise_scale | noise_w |
|----------|-------------|-------------|---------|
| suspense | 1.2         | 0.667       | 0.8     |
| action   | 0.8         | 0.3         | 0.4     |
| neutral  | 1.0         | 0.5         | 0.6     |
| anger    | 0.9         | 0.4         | 0.5     |
| fearful  | 1.1         | 0.7         | 0.75    |

**Responsibilities:**
- Map emotion names to Piper synthesis parameters
- Provide default (neutral) for unknown emotions
- Export config for generator module

---

### 3. Generator (`generator.py`)
**Input:** Text + SynthesisConfig  
**Output:** Raw WAV audio segment

Uses `piper-tts` Python package:

```python
from piper import PiperVoice

voice = PiperVoice.load(model_path)
audio = voice.synthesize(text, config=synthesis_config)
```

**Responsibilities:**
- Load Piper voice model
- Synthesize each utterance with emotion-specific config
- Output raw audio segments
- Handle synthesis errors gracefully

---

### 4. Post-Processor (`post_processor.py`)
**Input:** List of audio segments + pause metadata  
**Output:** Concatenated audio with injected silences

Uses `pydub` for silence injection:

```python
from pydub import AudioSegment

# Inject silence after each segment
silence = AudioSegment.silent(duration=ms)
final_audio = segment + silence + next_segment
```

**Pause Durations:**
- `short`: 250ms
- `medium`: 500ms  
- `long`: 1000ms
- `very_long`: 2000ms

**Responsibilities:**
- Concatenate audio segments in order
- Inject silence based on pause metadata
- Export final mixed audio

---

### 5. Output (`output.py`)
**Input:** Final mixed audio  
**Output:** Normalized MP3/WAV file

Uses `ffmpeg` for normalization:

```bash
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 output.mp3
```

**Responsibilities:**
- Loudness normalization (target: -16 LUFS)
- Format conversion (MP3, WAV, OGG)
- Metadata tagging (title, author, chapter)
- Final file output

---

## Data Flow

```
Input JSON → Parser → Emotion Mapper → Generator → Post-Processor → Output
                ↓           ↓              ↓            ↓
            Utterances   Config      Raw Audio    Mixed Audio
```

---

## Dependencies

```
piper-tts>=1.2.0
pydub>=0.25.1
ffmpeg-python>=0.2.0
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **No SSML** | Piper has poor SSML support; native params work better |
| **Post-gen pauses** | pydub silence injection is reliable and SSML-free |
| **5 modules max** | Forces clean boundaries, prevents over-engineering |
| **JSON input** | Simple, parseable, versionable |
| **ffmpeg normalization** | Industry standard loudness (LUFS) |

---

## Success Criteria

- [ ] 5 modules or fewer
- [ ] Zero SSML usage
- [ ] Emotion mapping via Piper native params
- [ ] Pause injection via pydub
- [ ] Normalized output audio
