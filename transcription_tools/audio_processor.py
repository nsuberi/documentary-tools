import asyncio
import tempfile
from typing import List, Dict
from pathlib import Path
from rich.progress import Progress, TaskID
from config import Config
from utils import compress_wav, get_output_filename, format_transcript
from aws_client import AWSTranscribeClient

class AudioProcessor:
    def __init__(self, aws_client: AWSTranscribeClient):
        self.aws_client = aws_client
        self.semaphore = asyncio.Semaphore(Config.MAX_CONCURRENT_JOBS)

    async def process_file(self, input_file: str, output_dir: str, 
                          progress: Progress, task_id: TaskID) -> None:
        """Process a single audio file."""
        try:
            # Create temporary file for compressed audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                compressed_file, duration = compress_wav(input_file, temp_file.name)
                
                # Upload to S3
                file_name = Path(input_file).stem
                s3_key = f"uploads/{file_name}.wav"
                file_uri = await self.aws_client.upload_to_s3(
                    compressed_file, "catching-vibes-audio-transcriptions", s3_key
                )
                
                # Start transcription
                job_name = f"transcription_{file_name}"
                await self.aws_client.start_transcription_job(job_name, file_uri)
                
                # Get results
                transcript = await self.aws_client.get_transcription_result(job_name)
                
                # Format and save transcript
                formatted_text = format_transcript(transcript)
                output_file = get_output_filename(input_file, output_dir)
                
                with open(output_file, 'w') as f:
                    f.write(formatted_text)
                
                progress.update(task_id, advance=1)
                
        except Exception as e:
            progress.console.print(f"Error processing {input_file}: {str(e)}")
            raise

    async def process_batch(self, files: List[str], output_dir: str) -> None:
        """Process a batch of audio files."""
        print("starting process_batch")
        progress = Progress()
        progress.start()
    
        print("made it in")
        task = progress.add_task(
            "[cyan]Processing audio files...", 
            total=len(files)
        )
        
        async def process_with_semaphore(file: str):
            async with self.semaphore:
                await self.process_file(file, output_dir, progress, task)
        
        tasks = [process_with_semaphore(file) for file in files]
        await asyncio.gather(*tasks, return_exceptions=True)
