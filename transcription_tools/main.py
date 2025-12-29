import asyncio
import argparse
from rich.console import Console
from transcriber import Transcriber

def parse_args():
    parser = argparse.ArgumentParser(description='Audio Transcription Tool')
    parser.add_argument('input_dir', help='Input directory containing WAV files')
    parser.add_argument('output_dir', help='Output directory for transcripts')
    return parser.parse_args()

async def main():
    console = Console()
    args = parse_args()

    try:
        transcriber = Transcriber()
        await transcriber.process_directory(args.input_dir, args.output_dir)
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
