import asyncio
import os
from typing import List
from pathlib import Path
from rich.console import Console
from config import Config
from audio_processor import AudioProcessor
from aws_client import AWSTranscribeClient
from utils import create_parallel_output_dir

class Transcriber:
    def __init__(self):
        self.console = Console()
        self.aws_client = AWSTranscribeClient()
        self.processor = AudioProcessor(self.aws_client)

    def find_wav_files(self, input_dir: str) -> List[str]:
        """Find all WAV files in the input directory."""
        self.console.print(f"[green]Looking for WAV files... in {input_dir}")
        wav_files = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.wav'):
                    wav_files.append(os.path.join(root, file))
        return wav_files

    def create_batches(self, files: List[str]) -> List[List[str]]:
        """Split files into batches."""
        return [files[i:i + Config.BATCH_SIZE] 
                for i in range(0, len(files), Config.BATCH_SIZE)]

    async def process_directory(self, input_dir: str, output_dir: str) -> None:
        """Process all WAV files in the input directory."""
        try:
            # Find all WAV files
            wav_files = self.find_wav_files(input_dir)
            if not wav_files:
                self.console.print("[yellow]No WAV files found in the input directory.")
                return

            self.console.print(f"[green]Found {len(wav_files)} WAV files to process.")

            # Create output directory structure
            output_dir = create_parallel_output_dir(input_dir, output_dir)

            # Process files in batches
            batches = self.create_batches(wav_files)
            for i, batch in enumerate(batches, 1):
                self.console.print(f"[cyan]Processing batch {i}/{len(batches)}...")
                await self.processor.process_batch(batch, output_dir)

            self.console.print("[green]Transcription completed successfully!")

        except Exception as e:
            self.console.print(f"[red]Error during transcription: {str(e)}")
            raise
