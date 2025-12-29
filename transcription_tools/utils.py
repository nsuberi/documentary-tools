import os
import wave
import audioop
from pathlib import Path
from typing import Tuple
from rich.console import Console
from datetime import datetime
from config import Config

console = Console()

def create_parallel_output_dir(input_path: str, base_output_dir: str) -> str:
    """Create parallel output directory structure."""
    rel_path = os.path.relpath(input_path, base_output_dir)
    output_path = os.path.join(base_output_dir, "transcripts", rel_path)
    os.makedirs(output_path, exist_ok=True)
    return output_path

def compress_wav(input_file: str, output_file: str) -> Tuple[str, int]:
    """Compress WAV file and return the path and duration."""
    with wave.open(input_file, 'rb') as wav_in:
        # Get original parameters
        channels = wav_in.getnchannels()
        width = wav_in.getsampwidth()
        rate = wav_in.getframerate()
        frames = wav_in.readframes(wav_in.getnframes())
        duration = wav_in.getnframes() / float(rate)

        # # Convert to mono if needed
        # if channels > 1:
        #     frames = audioop.tomono(frames, width, 1, 1)
        #     channels = 1

        # # Downsample if needed
        # if rate > Config.TARGET_SAMPLE_RATE:
        #     frames = audioop.ratecv(frames, width, 1, rate,
        #                           Config.TARGET_SAMPLE_RATE, None)[0]
        #     rate = Config.TARGET_SAMPLE_RATE

    # Write compressed file
    with wave.open(output_file, 'wb') as wav_out:
        wav_out.setnchannels(channels)
        wav_out.setsampwidth(width)
        wav_out.setframerate(rate)
        wav_out.writeframes(frames)

    return output_file, int(duration)

def get_output_filename(input_file: str, output_dir: str) -> str:
    """Generate output filename for transcript."""
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    timestamp = datetime.now().strftime(Config.TIMESTAMP_FORMAT)
    return os.path.join(output_dir, f"{base_name}_{timestamp}.txt")

def format_transcript(transcript: dict) -> str:
    """Format transcript with speaker labels."""
    formatted_lines = []
    current_speaker = None
    
    import boto3
    from urllib.parse import urlparse

    # Assuming 'transcript' contains the TranscriptFileUri
    s3_uri = transcript['TranscriptFileUri']

    print('parsing URI')
    # Parse the S3 URI
    parsed_uri = urlparse(s3_uri)
    bucket_name = parsed_uri.netloc
    object_key = parsed_uri.path.lstrip('/')

    print(parsed_uri, bucket_name, object_key)

    # Create an S3 client
    s3_client = boto3.client('s3')

    print('donwloading file')
    # Download the file
    local_file_name = 'downloaded_transcript.json'
    s3_client.download_file(bucket_name, object_key, local_file_name)

    # Now read the local file and parse it
    import json
    with open(local_file_name, 'r') as file:
        transcript_data = json.load(file)

    # Now you can iterate over the items
    for item in transcript_data['results']['items']:
        # Process each item
        print(f"item: {item}")

    print(f"Transcript: {transcript}")
    for item in transcript['items']:
        if 'speaker_label' in item and item['speaker_label'] != current_speaker:
            current_speaker = item['speaker_label']
            formatted_lines.append(f"\n[{current_speaker}]")
        
        if 'alternatives' in item and item['alternatives']:
            formatted_lines.append(item['alternatives'][0]['content'])
    
    return ' '.join(formatted_lines)
