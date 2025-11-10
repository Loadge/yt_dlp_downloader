# YouTube Downloader with yt-dlp

[![Docker Build](https://github.com/yourusername/yt-dlp-downloader/actions/workflows/docker-build.yml/badge.svg)](https://github.com/yourusername/yt-dlp-downloader/actions/workflows/docker-build.yml)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-red.svg)](https://github.com/yt-dlp/yt-dlp)

A powerful, Docker-ready Python application for batch downloading YouTube videos using yt-dlp. Configure your downloads with simple YAML files and run locally or in containers.

## ✨ Features

- 📝 **YAML Configuration** - Simple, readable config files
- 🎬 **Quality Control** - Per-video quality settings (4K, 1080p, 720p, etc.)
- 📄 **Subtitle Support** - Download subtitles in multiple languages
- 📋 **Playlist Support** - Download entire playlists with one entry
- 🍪 **Cookie Support** - Access age-restricted and members-only content
- 🎨 **Custom Formats** - Advanced format strings for power users
- 📊 **Progress Bars** - Real-time download progress
- 📝 **Comprehensive Logging** - Timestamped logs with file output
- 🤖 **JSON Output** - Automation-friendly JSON mode
- 🐳 **Docker Ready** - Optimized Docker images and compose files
- ♻️ **Skip Existing** - Automatically skip already downloaded videos
- 🔄 **Error Handling** - Continue on failures with detailed summary

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/yt-dlp-downloader.git
cd yt-dlp-downloader
```

2. **Create your config file:**
```bash
cp examples/basic.yaml config/videos.yaml
# Edit config/videos.yaml with your video URLs
```

3. **Run with Docker Compose:**
```bash
docker-compose up
```

The program will execute once and exit.

**For network storage (NAS, file servers):** See [NETWORK_DRIVES.md](NETWORK_DRIVES.md) for detailed setup instructions.

### Using Python

1. **Clone and install:**
```bash
git clone https://github.com/yourusername/yt-dlp-downloader.git
cd yt-dlp-downloader
pip install -r requirements.txt
```

2. **Install FFmpeg:**
   - Windows: `winget install FFmpeg`
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

3. **Create config and run:**
```bash
cp examples/basic.yaml config/videos.yaml
# Edit config/videos.yaml with your videos
python youtube_downloader.py

# Or specify a custom config file
python youtube_downloader.py my-videos.yaml
```

## 📋 Configuration

### Path Formats

The `target_folder` supports multiple path formats:

| Platform | Format | Example |
|----------|--------|---------|
| **Relative** | `./folder` or `folder` | `./downloads` |
| **Windows Local** | `C:\\path\\to\\folder` | `C:\\Users\\John\\Videos` |
| **Windows Network (UNC)** | `\\\\server\\share\\folder` | `\\\\FileServer\\Media\\Videos` |
| **Windows Network (Alt)** | `//server/share/folder` | `//FileServer/Media/Videos` |
| **Linux/Mac Local** | `/path/to/folder` | `/home/john/videos` |
| **Linux Mounted Drive** | `/mnt/path` | `/mnt/media/videos` |
| **Docker Volume** | `/mount/path` | `/downloads` |

**Important:** In YAML, backslashes must be escaped (`\\`) or use forward slashes (`/`)

### Basic Example

```yaml
target_folder: "./downloads"
default_quality: "1080p"

videos:
  - url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    name: "Rick Astley - Never Gonna Give You Up"
  
  - url: "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    name: "Me at the zoo"
    quality: "720p"
```

### Advanced Example

```yaml
target_folder: "./downloads"
default_quality: "1080p"
subtitles: "en"
cookies: "cookies.txt"

videos:
  # Simple video
  - url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    name: "My Video"
  
  # Custom quality
  - url: "https://www.youtube.com/watch?v=example1"
    name: "High Quality Video"
    quality: "1440p"
  
  # Multiple subtitle languages
  - url: "https://www.youtube.com/watch?v=example2"
    name: "Multi-language Video"
    subtitles: ["en", "es", "fr"]
  
  # Entire playlist
  - url: "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
    name: "Python Tutorials"
    is_playlist: true
    quality: "720p"
  
  # Audio only
  - url: "https://www.youtube.com/watch?v=example3"
    name: "Podcast Episode"
    quality: "audio"
  
  # Advanced format string
  - url: "https://www.youtube.com/watch?v=example4"
    name: "Custom Format"
    format: "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
```

See [examples/](examples/) for more configuration examples.

## 🐳 Docker Usage

### Quick Start

```bash
# Default: downloads to ./downloads folder
docker-compose up
```

### Network Storage (NAS, File Servers)

To download directly to network storage:

1. **Map your network share to a drive letter in Windows** (e.g., Z:)
   - See detailed guide: [NETWORK_DRIVES.md](NETWORK_DRIVES.md)

2. **Update `docker-compose.yml`:**
   ```yaml
   volumes:
     - Z:\Videos:/downloads  # Your mapped drive
   ```

3. **Run Docker:**
   ```bash
   docker-compose up
   ```

📖 **Full Docker documentation:** [DOCKER.md](DOCKER.md)

### Docker Compose

```bash
# Run once and exit
docker-compose up

# View logs after completion
docker-compose logs

# Remove the container
docker-compose down
```

### Docker CLI

```bash
# Build
docker build -t yt-downloader .

# Run
docker run --rm \
  -v $(pwd)/config:/config:ro \
  -v $(pwd)/downloads:/downloads \
  yt-downloader

# With logging
docker run --rm \
  -v $(pwd)/config:/config:ro \
  -v $(pwd)/downloads:/downloads \
  -v $(pwd)/logs:/logs \
  -e LOG_PATH=/logs \
  yt-downloader

# JSON output
docker run --rm \
  -v $(pwd)/config:/config:ro \
  -v $(pwd)/downloads:/downloads \
  -e JSON_OUTPUT=true \
  yt-downloader > results.json
```

See [DOCKER.md](DOCKER.md) for comprehensive Docker documentation.

## 💻 Command Line Options

```bash
# Use default config (config/videos.yaml)
python youtube_downloader.py

# Specify custom config file
python youtube_downloader.py my-videos.yaml

# With log file
python youtube_downloader.py config/videos.yaml --log-file download.log

# JSON output mode
python youtube_downloader.py config/videos.yaml --json

# Both
python youtube_downloader.py config/videos.yaml --json --log-file download.log > results.json
```

## 📊 Output Examples

### Console Output
```
2024-11-01 14:30:15 - INFO - Loading configuration from: videos.yaml
2024-11-01 14:30:15 - INFO - Target folder: /downloads
2024-11-01 14:30:15 - INFO - Processing 3 video(s)...
2024-11-01 14:30:15 - INFO - [1/3] Processing: My Video
2024-11-01 14:30:15 - INFO - URL: https://youtube.com/watch?v=...
  Progress: 45.2% of 125.3MB at 2.5MB/s ETA: 00:35
2024-11-01 14:31:00 - INFO - Status: SUCCESS (took 45.23s)

============================================================
DOWNLOAD SUMMARY
============================================================
Total videos processed: 3
Successfully downloaded: 2
Skipped (already exist): 1
Failed: 0
============================================================
```

### JSON Output
```json
{
  "start_time": "2024-11-01T14:30:15.123456",
  "config_file": "videos.yaml",
  "target_folder": "/downloads",
  "total_videos": 3,
  "successful": [
    {
      "name": "My Video",
      "url": "https://youtube.com/watch?v=...",
      "duration": 45.23,
      "timestamp": "2024-11-01T14:31:00.456789"
    }
  ],
  "skipped": [],
  "failed": [],
  "end_time": "2024-11-01T14:35:30.789012"
}
```

## 🎯 Quality Options

| Quality | Description |
|---------|-------------|
| `best` | Best available quality (default) |
| `2160p` | 4K (2160p) |
| `1440p` | 2K (1440p) |
| `1080p` | Full HD |
| `720p` | HD |
| `480p` | SD |
| `360p` | Low quality |
| `audio` | Audio only (best quality) |

## 🍪 Cookie Support

For age-restricted or members-only videos:

1. Install browser extension: "Get cookies.txt"
2. Export cookies while logged into YouTube
3. Save as `cookies.txt` in project directory
4. Reference in YAML config:
```yaml
cookies: "cookies.txt"
```

## 📁 Project Structure

```
yt-dlp-downloader/
├── youtube_downloader.py    # Main application
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── docker-entrypoint.sh    # Container entry point
├── .dockerignore          # Docker build exclusions
├── README.md              # This file
├── DOCKER.md              # Docker documentation
├── NETWORK_DRIVES.md      # Network drives setup guide
├── LICENSE                # MIT License
├── .github/
│   └── workflows/
│       └── docker-build.yml  # CI/CD pipeline
├── examples/
│   ├── basic.yaml         # Basic example config
│   ├── advanced.yaml      # Advanced example config
│   └── playlist.yaml      # Playlist example
├── config/                # Your config files (create this)
├── downloads/             # Downloaded videos (auto-created)
└── logs/                  # Log files (auto-created)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The powerful YouTube downloader
- [FFmpeg](https://ffmpeg.org/) - Multimedia framework

## ⚠️ Legal Notice

This tool is for personal use only. Please respect YouTube's Terms of Service and copyright laws. Only download videos you have permission to download.

## 🐛 Issues and Support

If you encounter any problems or have questions:

1. Check the [DOCKER.md](DOCKER.md) documentation
2. Review existing [GitHub Issues](https://github.com/yourusername/yt-dlp-downloader/issues)
3. Create a new issue with detailed information

## 🔄 Updates

To update to the latest version:

```bash
# Python
git pull
pip install -r requirements.txt --upgrade

# Docker
docker-compose pull
docker-compose up -d
```

## 📈 Roadmap

- [ ] Web UI for easy configuration
- [ ] Scheduled downloads with cron support
- [ ] Download queue management
- [ ] Multiple config file support
- [ ] Watch folder mode
- [ ] Rate limiting options
- [ ] Retry logic for failed downloads
