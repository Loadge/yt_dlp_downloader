# Docker Setup Guide

## Quick Start

### Using Docker Compose (Recommended)

1. **Create directory structure:**
```bash
mkdir -p config downloads logs
```

2. **Create your config file:**
```bash
# Create config/videos.yaml with your video list
```

3. **Configure volumes in docker-compose.yml** (see "Volume Configuration" section below)

4. **Run with docker-compose:**
```bash
docker-compose up
```

The program will execute once, download all videos from your config, and exit.

## Volume Configuration

### Local Downloads (Default)

By default, videos are downloaded to `./downloads` in your project directory:

```yaml
volumes:
  - ./downloads:/downloads
```

Your `videos.yaml` should use:
```yaml
target_folder: "/downloads"
```

### Windows Mapped Network Drives (Recommended for Network Storage)

To download directly to network storage (NAS, file servers, etc.):

#### Step 1: Map Network Drive in Windows

1. Open File Explorer
2. Right-click on "This PC" → "Map network drive..."
3. Choose a drive letter (e.g., `Z:`)
4. Enter your network path: `\\ServerName\ShareName\Folder`
5. Check "Reconnect at sign-in" (optional but recommended)
6. Click "Finish"

**Example:** Map `\\NAS_1\data` to `Z:`

#### Step 2: Update docker-compose.yml

Uncomment and modify the volume mount:

```yaml
volumes:
  - ./config:/config:ro
  # Comment out or remove the default local mount
  # - ./downloads:/downloads
  
  # Add your mapped drive
  - Z:\03 Peliculas, Libros, Series\00 PELIS:/downloads
  
  - ./logs:/logs
```

#### Step 3: Update videos.yaml

Use the container path:

```yaml
target_folder: "/downloads"
```

### Multiple Mapped Drives Examples

```yaml
# Movies on Z: drive
- Z:\Movies:/downloads

# TV Shows on Y: drive  
- Y:\TV Shows:/downloads

# Backup drive X:
- X:\Backup\Videos:/downloads

# Subfolder in mapped drive
- Z:\Media\YouTube:/downloads
```

### Local Windows Folders (Absolute Paths)

You can also mount any local Windows folder:

```yaml
volumes:
  - C:\Users\YourName\Videos:/downloads
  - D:\Media\Downloads:/downloads
```

## Important Notes for Network Drives

⚠️ **CRITICAL:** 
- Docker CANNOT mount UNC paths directly (`\\ServerName\ShareName`)
- You MUST map the network share to a drive letter first (Z:, Y:, X:, etc.)
- The mapped drive must be connected before starting Docker
- If the drive disconnects, Docker won't be able to access it

✅ **Works:**
```yaml
- Z:\Videos:/downloads           # Mapped drive
- C:\Users\John\Videos:/downloads # Local absolute path
- ./downloads:/downloads          # Relative path
```

❌ **Does NOT work:**
```yaml
- \\NAS_1\data\Videos:/downloads  # UNC path - will fail!
```

### Using Docker CLI

1. **Build the image:**
```bash
docker build -t yt-downloader .
```

2. **Run the container:**
```bash
docker run --rm \
  -v $(pwd)/config:/config:ro \
  -v $(pwd)/downloads:/downloads \
  -v $(pwd)/logs:/logs \
  yt-downloader
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CONFIG_PATH` | `/config/videos.yaml` | Path to YAML config file |
| `DOWNLOAD_PATH` | `/downloads` | Download destination directory |
| `LOG_PATH` | `/logs` | Log file directory |
| `JSON_OUTPUT` | `false` | Enable JSON output mode |
| `PUID` | `1000` | User ID for file permissions |
| `PGID` | `1000` | Group ID for file permissions |

## Volume Mounts

### Required Volumes

- **`./config:/config:ro`** - Mount your config directory (read-only)
- **`./downloads:/downloads`** - Mount download directory

### Optional Volumes

- **`./logs:/logs`** - Mount logs directory
- **`./cookies.txt:/app/cookies.txt:ro`** - Mount cookies file for authenticated downloads

## Usage Examples

### Basic Usage

```bash
docker run --rm \
  -v $(pwd)/config:/config:ro \
  -v $(pwd)/downloads:/downloads \
  yt-downloader
```

### With Logging

```bash
docker run --rm \
  -v $(pwd)/config:/config:ro \
  -v $(pwd)/downloads:/downloads \
  -v $(pwd)/logs:/logs \
  -e LOG_PATH=/logs \
  yt-downloader
```

### JSON Output Mode

```bash
docker run --rm \
  -v $(pwd)/config:/config:ro \
  -v $(pwd)/downloads:/downloads \
  -e JSON_OUTPUT=true \
  yt-downloader > results.json
```

### With Cookies for Authentication

```bash
docker run --rm \
  -v $(pwd)/config:/config:ro \
  -v $(pwd)/downloads:/downloads \
  -v $(pwd)/cookies.txt:/app/cookies.txt:ro \
  yt-downloader
```

### Custom File Permissions

```bash
docker run --rm \
  -v $(pwd)/config:/config:ro \
  -v $(pwd)/downloads:/downloads \
  -e PUID=$(id -u) \
  -e PGID=$(id -g) \
  yt-downloader
```

## Docker Compose Examples

### Basic Setup

```yaml
version: '3.8'
services:
  yt-downloader:
    image: yt-downloader:latest
    volumes:
      - ./config:/config:ro
      - ./downloads:/downloads
```

### With All Features

```yaml
version: '3.8'
services:
  yt-downloader:
    image: yt-downloader:latest
    environment:
      - JSON_OUTPUT=false
      - PUID=1000
      - PGID=1000
    volumes:
      - ./config:/config:ro
      - ./downloads:/downloads
      - ./logs:/logs
      - ./cookies.txt:/app/cookies.txt:ro
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## Health Check

The container includes a health check that runs every 30 seconds. Check container health with:

```bash
docker ps
# or
docker inspect --format='{{.State.Health.Status}}' yt-downloader
```

## Image Size Optimization

The Docker image uses multi-stage builds and includes:
- Python 3.12 slim base image
- Only essential dependencies
- Cleaned apt cache
- Virtual environment for Python packages

Typical image size: ~300-400MB (much smaller than full Python images)

## Troubleshooting

### Config file not found
```
Error: Configuration file not found at /config/videos.yaml
```
**Solution:** Ensure you're mounting the config directory correctly and the file exists.

### Permission denied on downloads
**Solution:** Set `PUID` and `PGID` environment variables to match your user:
```bash
-e PUID=$(id -u) -e PGID=$(id -g)
```

### FFmpeg errors
The image includes FFmpeg. If you encounter issues, verify with:
```bash
docker run --rm yt-downloader ffmpeg -version
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Download Videos
  run: |
    docker run --rm \
      -v ${{ github.workspace }}/config:/config:ro \
      -v ${{ github.workspace }}/downloads:/downloads \
      -e JSON_OUTPUT=true \
      yt-downloader > results.json
```

### GitLab CI Example

```yaml
download_videos:
  image: yt-downloader:latest
  script:
    - python /app/youtube_downloader.py /config/videos.yaml --json
  artifacts:
    paths:
      - downloads/
```

## Building for Production

### Build with version tag
```bash
docker build -t yt-downloader:1.0.0 .
docker tag yt-downloader:1.0.0 yt-downloader:latest
```

### Push to registry
```bash
docker tag yt-downloader:latest username/yt-downloader:latest
docker push username/yt-downloader:latest
```

## Security Considerations

- Container runs as non-root user (UID 1000)
- Config and cookies mounted as read-only
- No unnecessary ports exposed
- Minimal attack surface with slim base image
- Regular security updates via base image updates