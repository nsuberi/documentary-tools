"""
YouTube Video Downloader Script - DaVinci Resolve ProRes Workflow
Downloads YouTube videos and converts to ProRes while keeping originals.

Requirements:
    pip install yt-dlp
    FFmpeg must be installed and in system PATH
    
    Install FFmpeg:
    - Windows: Download from ffmpeg.org or use: winget install ffmpeg
    - Mac: brew install ffmpeg
    - Linux: sudo apt install ffmpeg

Usage:
    python download_videos.py
"""

import os
import sys
import subprocess
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed.")
    print("Please install it using: pip install yt-dlp")
    sys.exit(1)


def check_ffmpeg():
    """Check if FFmpeg is installed and available"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def convert_to_prores(input_file, output_folder, prores_profile='422'):
    """
    Convert video file to ProRes using FFmpeg.
    
    Args:
        input_file (str): Path to input video file
        output_folder (str): Path to output folder for ProRes files
        prores_profile (str): ProRes profile to use
            - '422_proxy': ProRes 422 Proxy (smallest, for proxies)
            - '422_lt': ProRes 422 LT (light, good for most editing)
            - '422': ProRes 422 (standard, recommended)
            - '422_hq': ProRes 422 HQ (high quality, better for color grading)
            - '4444': ProRes 4444 (highest quality with alpha support)
    
    Returns:
        str: Path to converted file or None if failed
    """
    # Create ProRes subfolder
    prores_folder = os.path.join(output_folder, 'ProRes')
    Path(prores_folder).mkdir(parents=True, exist_ok=True)
    
    # Set ProRes profile number for FFmpeg
    profile_map = {
        '422_proxy': '0',
        '422_lt': '1',
        '422': '2',
        '422_hq': '3',
        '4444': '4',
        '4444_xq': '5'
    }
    
    profile_num = profile_map.get(prores_profile, '2')
    
    # Generate output filename
    input_name = Path(input_file).stem
    output_file = os.path.join(prores_folder, f"{input_name}_ProRes_{prores_profile}.mov")
    
    # Build FFmpeg command
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'prores_ks',  # ProRes encoder
        '-profile:v', profile_num,
        '-vendor', 'apl0',  # Apple vendor code
        '-pix_fmt', 'yuv422p10le' if prores_profile != '4444' else 'yuva444p10le',
        '-c:a', 'pcm_s16le',  # Uncompressed audio
        '-y',  # Overwrite output file if exists
        output_file
    ]
    
    print(f"\n  Converting to ProRes {prores_profile}...")
    print(f"  This may take a few minutes depending on video length...")
    
    try:
        # Run FFmpeg conversion
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Get file sizes for comparison
        original_size = os.path.getsize(input_file) / (1024 * 1024)  # MB
        prores_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        
        print(f"  ✓ ProRes conversion complete!")
        print(f"  Original MP4: {original_size:.1f} MB")
        print(f"  ProRes file: {prores_size:.1f} MB ({prores_size/original_size:.1f}x larger)")
        print(f"  Saved to: {output_file}")
        
        return output_file
        
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Conversion failed: {e.stderr}")
        return None
    except Exception as e:
        print(f"  ✗ Conversion error: {str(e)}")
        return None


def download_youtube_videos(video_urls, destination_folder, convert_to_prores_flag=True, prores_profile='422'):
    """
    Download YouTube videos and optionally convert to ProRes.
    
    Args:
        video_urls (list): List of YouTube video URLs
        destination_folder (str): Path to destination folder
        convert_to_prores_flag (bool): Whether to convert to ProRes after download
        prores_profile (str): ProRes profile for conversion
    """
    # Create destination folder if it doesn't exist
    Path(destination_folder).mkdir(parents=True, exist_ok=True)
    
    # Check FFmpeg if conversion is enabled
    if convert_to_prores_flag and not check_ffmpeg():
        print("ERROR: FFmpeg is not installed or not in system PATH.")
        print("ProRes conversion requires FFmpeg.")
        print("\nInstall FFmpeg:")
        print("  Windows: winget install ffmpeg  OR download from ffmpeg.org")
        print("  Mac: brew install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
        sys.exit(1)
    
    # Configure download options
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),
        'progress_hooks': [download_progress_hook],
        'ignoreerrors': True,
    }
    
    # Track results
    downloaded = 0
    converted = 0
    failed_download = 0
    failed_conversion = 0
    
    print(f"\nStarting download of {len(video_urls)} video(s)...")
    print(f"Destination: {os.path.abspath(destination_folder)}")
    if convert_to_prores_flag:
        print(f"ProRes Profile: {prores_profile}")
        print(f"Note: Original MP4 files will be kept in the main folder")
        print(f"      ProRes files will be in the 'ProRes' subfolder\n")
    else:
        print()
    
    # Download each video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(video_urls, 1):
            print(f"[{i}/{len(video_urls)}] Processing: {url}")
            try:
                info = ydl.extract_info(url, download=False)
                print(f"Title: {info.get('title', 'Unknown')}")
                print(f"Duration: {info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}")
                
                # Download the video
                result = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(result)
                
                downloaded += 1
                print(f"✓ Download complete: {downloaded_file}\n")
                
                # Convert to ProRes if enabled
                if convert_to_prores_flag:
                    prores_file = convert_to_prores(
                        downloaded_file, 
                        destination_folder, 
                        prores_profile
                    )
                    if prores_file:
                        converted += 1
                    else:
                        failed_conversion += 1
                
                print()  # Extra line break between videos
                
            except Exception as e:
                failed_download += 1
                print(f"✗ Failed to download: {str(e)}\n")
    
    # Print summary
    print("\n" + "="*70)
    print("DOWNLOAD & CONVERSION SUMMARY")
    print("="*70)
    print(f"Total videos requested: {len(video_urls)}")
    print(f"Successfully downloaded: {downloaded}")
    print(f"Failed downloads: {failed_download}")
    if convert_to_prores_flag:
        print(f"Successfully converted to ProRes: {converted}")
        print(f"Failed conversions: {failed_conversion}")
    print("="*70)
    print("\nFile Organization:")
    print(f"  Original MP4 files: {os.path.abspath(destination_folder)}")
    if convert_to_prores_flag:
        print(f"  ProRes files: {os.path.abspath(os.path.join(destination_folder, 'ProRes'))}")
    print("\nDaVinci Resolve Tips:")
    print("  - Import ProRes files for smooth editing and color grading")
    print("  - Keep MP4 originals as backup or for quick previews")
    print("  - ProRes files will match your existing project codec")
    if prores_profile == '422':
        print("  - ProRes 422 is perfect for most editing workflows")
    elif prores_profile == '422_hq':
        print("  - ProRes 422 HQ is ideal for heavy color grading")
    print("="*70)


def download_progress_hook(d):
    """Hook to show download progress"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        print(f"\rDownloading: {percent} | Speed: {speed} | ETA: {eta}", end='')
    elif d['status'] == 'finished':
        print(f"\rDownload complete, processing...                    ")


def main():
    """Main function with example usage"""
    
    # Example: Define your video URLs here
    video_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Replace with actual URLs
        # Add more URLs here
    ]
    
    # Define destination folder
    destination_folder = "./downloaded_videos"  # Change this to your desired path
    
    # ProRes conversion settings
    convert_to_prores_enabled = True  # Set to False to skip ProRes conversion
    
    # Choose ProRes profile:
    # '422_proxy' - Smallest, good for proxies (rough editing)
    # '422_lt' - Light, good for most editing
    # '422' - Standard quality (RECOMMENDED for most projects)
    # '422_hq' - High quality (better for heavy color grading)
    # '4444' - Highest quality with alpha channel support
    prores_profile = '422'
    
    # Alternative: Load URLs from a text file
    # Uncomment the following to read URLs from a file (one URL per line)
    """
    with open('video_urls.txt', 'r') as f:
        video_urls = [line.strip() for line in f if line.strip()]
    """
    
    # Download and convert videos
    if not video_urls:
        print("Error: No video URLs provided.")
        print("Please add URLs to the video_urls list or load them from a file.")
        sys.exit(1)
    
    download_youtube_videos(
        video_urls, 
        destination_folder, 
        convert_to_prores_enabled,
        prores_profile
    )


if __name__ == "__main__":
    main()
