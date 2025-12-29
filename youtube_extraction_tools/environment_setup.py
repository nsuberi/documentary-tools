#!/bin/bash
# YouTube Downloader Setup for Mac

echo "Setting up YouTube downloader environment..."

# Install Homebrew if not installed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install FFmpeg
echo "Installing FFmpeg..."
brew install ffmpeg

# Install yt-dlp
echo "Installing yt-dlp..."
pip3 install --upgrade yt-dlp

# Create folders
mkdir -p downloaded_videos/ProRes

# Create sample URLs file
cat > video_urls.txt << 'EOF'
# Add your YouTube URLs here, one per line
# https://www.youtube.com/watch?v=example
EOF

echo "✓ Setup complete! Edit video_urls.txt and run: python3 download_videos.py"
