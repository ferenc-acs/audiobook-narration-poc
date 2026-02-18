#!/usr/bin/env python3
"""CLI entry point for audiobook narrator."""

import argparse
import json
import sys
from pathlib import Path

from narrator.input_parser import InputParser
from narrator.emotion_config import EmotionMapper
from narrator.piper_wrapper import PiperWrapper
from narrator.post_processor import PostProcessor


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate emotional audiobook narration using Piper TTS"
    )
    parser.add_argument(
        'input',
        help='Input JSON file with narration segments'
    )
    parser.add_argument(
        '-o', '--output',
        default='output.mp3',
        help='Output audio file (default: output.mp3)'
    )
    parser.add_argument(
        '-m', '--model',
        required=True,
        help='Path to Piper voice model (.onnx file)'
    )
    parser.add_argument(
        '-c', '--config',
        default='config/emotions.json',
        help='Path to emotions config JSON'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['mp3', 'wav', 'ogg'],
        default='mp3',
        help='Output audio format'
    )
    parser.add_argument(
        '--no-normalize',
        action='store_true',
        help='Skip loudness normalization'
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Validate model exists
    if not Path(args.model).exists():
        print(f"Error: Piper model not found: {args.model}", file=sys.stderr)
        sys.exit(1)
    
    # Validate config exists
    if not Path(args.config).exists():
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)
    
    print(f"🎙️  Audiobook Narrator")
    print(f"   Input: {args.input}")
    print(f"   Model: {args.model}")
    print(f"   Output: {args.output}")
    print()
    
    try:
        # Initialize components
        print("Loading emotion config...")
        emotion_mapper = EmotionMapper(args.config)
        
        print(f"Loading Piper model...")
        piper = PiperWrapper(args.model)
        
        print("Parsing input...")
        input_parser = InputParser()
        segments = input_parser.parse_file(args.input)
        print(f"   Found {len(segments)} segments")
        print(f"   Emotions: {set(s.emotion for s in segments)}")
        print()
        
        # Generate audio for each segment
        print("Generating audio segments...")
        audio_segments = []
        pause_durations = []
        
        for i, segment in enumerate(segments):
            emotion_config = emotion_mapper.get_config(segment.emotion)
            pause_ms = emotion_mapper.get_pause_ms(segment.pause_after)
            
            print(f"   [{i+1}/{len(segments)}] {segment.emotion}: '{segment.text[:50]}...'")
            
            audio_bytes = piper.synthesize(segment.text, emotion_config)
            audio_segments.append(audio_bytes)
            pause_durations.append(pause_ms)
        
        print()
        print("Concatenating and adding pauses...")
        post_processor = PostProcessor()
        combined = post_processor.concatenate_segments(
            audio_segments,
            pause_durations
        )
        
        print(f"Exporting to {args.output}...")
        post_processor.export_to_file(
            combined,
            args.output,
            format=args.format,
            normalize=not args.no_normalize
        )
        
        print()
        print(f"✅ Done! Output saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
