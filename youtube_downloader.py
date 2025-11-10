import os
import sys
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed.")
    print("Please install it using: pip install yt-dlp")
    sys.exit(1)


class CustomLogger:
    """Custom logger that supports both file and console output."""
    
    def __init__(self, log_file=None, json_mode=False):
        self.log_file = log_file
        self.json_mode = json_mode
        self.json_logs = []
        
        if log_file and not json_mode:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger(__name__)
        elif not json_mode:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler()]
            )
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None
    
    def info(self, message):
        """Log info message."""
        if self.json_mode:
            self.json_logs.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'INFO',
                'message': message
            })
        else:
            self.logger.info(message)
    
    def warning(self, message):
        """Log warning message."""
        if self.json_mode:
            self.json_logs.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'WARNING',
                'message': message
            })
        else:
            self.logger.warning(message)
    
    def error(self, message):
        """Log error message."""
        if self.json_mode:
            self.json_logs.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'ERROR',
                'message': message
            })
        else:
            self.logger.error(message)
    
    def get_json_logs(self):
        """Return all JSON logs."""
        return self.json_logs


class ProgressLogger:
    """Custom progress hook for yt-dlp to show download progress."""
    
    def __init__(self, json_mode=False):
        self.json_mode = json_mode
        self.current_video = None
    
    def __call__(self, d):
        if self.json_mode:
            return
        
        if d['status'] == 'downloading':
            try:
                percent = d.get('_percent_str', 'N/A')
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                downloaded = d.get('_downloaded_bytes_str', 'N/A')
                total = d.get('_total_bytes_str', 'N/A')
                
                # Clear line and print progress
                print(f'\r  Progress: {percent} of {total} at {speed} ETA: {eta}', end='', flush=True)
            except:
                pass
        elif d['status'] == 'finished':
            print('\r  Progress: Download complete, processing...', flush=True)


def load_config(config_path):
    """Load and validate the YAML configuration file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not config:
            print("Error: Configuration file is empty.")
            sys.exit(1)
        
        if 'target_folder' not in config:
            print("Error: 'target_folder' not specified in config.")
            sys.exit(1)
        
        if 'videos' not in config or not isinstance(config['videos'], list):
            print("Error: 'videos' list not found or invalid in config.")
            sys.exit(1)
        
        return config
    
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)


def get_quality_format(quality):
    """Convert quality string to yt-dlp format string."""
    quality_map = {
        'best': 'bestvideo+bestaudio/best',
        '2160p': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
        '1440p': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
        '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
        'audio': 'bestaudio/best',
    }
    
    return quality_map.get(quality.lower(), quality)


def prepare_subtitle_options(subtitles_config):
    """Prepare subtitle download options."""
    if not subtitles_config:
        return {}
    
    opts = {}
    
    if subtitles_config == 'auto' or subtitles_config is True:
        opts['writesubtitles'] = True
        opts['writeautomaticsub'] = True
        opts['subtitleslangs'] = ['en']
    elif isinstance(subtitles_config, str):
        opts['writesubtitles'] = True
        opts['writeautomaticsub'] = True
        opts['subtitleslangs'] = [subtitles_config]
    elif isinstance(subtitles_config, list):
        opts['writesubtitles'] = True
        opts['writeautomaticsub'] = True
        opts['subtitleslangs'] = subtitles_config
    elif isinstance(subtitles_config, dict):
        opts['writesubtitles'] = subtitles_config.get('enabled', True)
        opts['writeautomaticsub'] = subtitles_config.get('auto', True)
        langs = subtitles_config.get('languages', ['en'])
        opts['subtitleslangs'] = langs if isinstance(langs, list) else [langs]
    
    return opts


def download_video(url, output_path, filename, video_config, global_config, logger, json_mode=False):
    """Download a single video or playlist using yt-dlp."""
    
    start_time = datetime.now()
    
    # Determine quality
    quality = video_config.get('quality', global_config.get('default_quality', 'best'))
    format_string = video_config.get('format', get_quality_format(quality))
    
    # Base options
    ydl_opts = {
        'format': format_string,
        'outtmpl': str(output_path / f'{filename}.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': json_mode,
        'no_warnings': json_mode,
        'progress_hooks': [ProgressLogger(json_mode=json_mode)],
    }
    
    # Handle playlists
    if video_config.get('is_playlist', False):
        ydl_opts['outtmpl'] = str(output_path / filename / '%(playlist_index)s - %(title)s.%(ext)s')
        ydl_opts['ignoreerrors'] = True
    
    # Subtitle options
    subtitles = video_config.get('subtitles', global_config.get('subtitles'))
    if subtitles:
        subtitle_opts = prepare_subtitle_options(subtitles)
        ydl_opts.update(subtitle_opts)
    
    # Cookie file support
    cookies = video_config.get('cookies', global_config.get('cookies'))
    if cookies:
        cookie_path = Path(cookies)
        if cookie_path.exists():
            ydl_opts['cookiefile'] = str(cookie_path)
        else:
            logger.warning(f"Cookie file not found: {cookies}")
    
    # Thumbnail download
    if video_config.get('thumbnail', global_config.get('download_thumbnails', False)):
        ydl_opts['writethumbnail'] = True
    
    # Metadata
    if video_config.get('metadata', global_config.get('write_metadata', False)):
        ydl_opts['writeinfojson'] = True
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Check if it's a playlist
            if 'entries' in info:
                video_count = len(list(info['entries']))
                logger.info(f"Detected playlist with {video_count} videos")
                if not video_config.get('is_playlist', False):
                    logger.warning("This is a playlist. Set 'is_playlist: true' to download all videos.")
                    logger.info("Downloading only the first video...")
                    ydl_opts['noplaylist'] = True
            
            ydl.download([url])
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return True, None, duration
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        return False, str(e), duration


def check_video_exists(target_folder, filename, is_playlist=False):
    """Check if video already exists in target folder."""
    target_path = Path(target_folder)
    
    # For playlists, check if the folder exists and has files
    if is_playlist:
        playlist_folder = target_path / filename
        if playlist_folder.exists() and playlist_folder.is_dir():
            files = list(playlist_folder.glob('*'))
            if files:
                return True
        return False
    
    # Check for common video extensions
    extensions = ['.mp4', '.mkv', '.webm', '.avi', '.mov', '.flv']
    
    for ext in extensions:
        if (target_path / f'{filename}{ext}').exists():
            return True
    
    return False


def main():
    # Check if config file path is provided
    if len(sys.argv) < 2:
        print("Usage: python youtube_downloader.py <config.yaml> [--json] [--log-file <path>]")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    # Parse command line arguments
    json_mode = '--json' in sys.argv
    log_file = None
    
    if '--log-file' in sys.argv:
        log_file_idx = sys.argv.index('--log-file')
        if log_file_idx + 1 < len(sys.argv):
            log_file = sys.argv[log_file_idx + 1]
    
    # Initialize logger
    logger = CustomLogger(log_file=log_file, json_mode=json_mode)
    
    # Load configuration
    logger.info(f"Loading configuration from: {config_path}")
    config = load_config(config_path)
    
    target_folder_str = config['target_folder']
    print(f"Target folder from config: {target_folder_str}")
    
    # Handle both absolute and relative paths correctly
    # Don't use Path() on Windows UNC paths or absolute paths from config
    if target_folder_str.startswith('\\\\') or target_folder_str.startswith('//'):
        # UNC path (network share)
        target_folder = Path(target_folder_str)
    elif len(target_folder_str) > 1 and target_folder_str[1] == ':':
        # Windows absolute path (e.g., C:\Users\...)
        target_folder = Path(target_folder_str)
    elif target_folder_str.startswith('/') and not target_folder_str.startswith('./'):
        # Unix absolute path
        target_folder = Path(target_folder_str)
    else:
        # Relative path - use Path normally
        target_folder = Path(target_folder_str)
    
    print(f"Resolved target folder path: {target_folder}")
    videos = config['videos']
    
    # Create target folder if it doesn't exist
    target_folder.mkdir(parents=True, exist_ok=True)
    logger.info(f"Target folder: {target_folder.absolute()}")
    
    # Display global settings
    if config.get('default_quality'):
        logger.info(f"Default quality: {config['default_quality']}")
    if config.get('subtitles'):
        logger.info(f"Subtitles: {config['subtitles']}")
    if config.get('cookies'):
        logger.info(f"Using cookies: {config['cookies']}")
    
    # Track results
    results = {
        'start_time': datetime.now().isoformat(),
        'config_file': config_path,
        'target_folder': str(target_folder.absolute()),
        'total_videos': len(videos),
        'successful': [],
        'skipped': [],
        'failed': []
    }
    
    total_videos = len(videos)
    
    logger.info(f"Processing {total_videos} video(s)...")
    
    for idx, video in enumerate(videos, 1):
        if not isinstance(video, dict) or 'url' not in video or 'name' not in video:
            logger.error(f"[{idx}/{total_videos}] Invalid entry: {video}")
            results['failed'].append({
                'entry': str(video),
                'error': 'Invalid format (missing url or name)',
                'timestamp': datetime.now().isoformat()
            })
            continue
        
        url = video['url']
        name = video['name']
        is_playlist = video.get('is_playlist', False)
        
        logger.info(f"[{idx}/{total_videos}] Processing: {name}")
        logger.info(f"URL: {url}")
        
        # Display video-specific settings
        if video.get('quality'):
            logger.info(f"Quality: {video['quality']}")
        if video.get('format'):
            logger.info(f"Format: {video['format']}")
        if video.get('subtitles'):
            logger.info(f"Subtitles: {video['subtitles']}")
        if is_playlist:
            logger.info(f"Type: Playlist")
        
        # Check if video already exists
        if check_video_exists(target_folder, name, is_playlist):
            logger.info(f"Status: SKIPPED (already exists)")
            results['skipped'].append({
                'name': name,
                'url': url,
                'timestamp': datetime.now().isoformat()
            })
            continue
        
        # Download video
        success, error, duration = download_video(url, target_folder, name, video, config, logger, json_mode)
        
        if success:
            logger.info(f"Status: SUCCESS (took {duration:.2f}s)")
            results['successful'].append({
                'name': name,
                'url': url,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.error(f"Status: FAILED - {error}")
            results['failed'].append({
                'name': name,
                'url': url,
                'error': error,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
    
    results['end_time'] = datetime.now().isoformat()
    results['logs'] = logger.get_json_logs() if json_mode else []
    
    # Output results
    if json_mode:
        print(json.dumps(results, indent=2))
    else:
        # Print summary
        print("\n" + "=" * 60)
        print("DOWNLOAD SUMMARY")
        print("=" * 60)
        print(f"Total videos processed: {results['total_videos']}")
        print(f"Successfully downloaded: {len(results['successful'])}")
        print(f"Skipped (already exist): {len(results['skipped'])}")
        print(f"Failed: {len(results['failed'])}")
        
        if results['skipped']:
            print("\nSkipped videos:")
            for item in results['skipped']:
                print(f"  - {item['name']}")
        
        if results['failed']:
            print("\nFailed downloads:")
            for item in results['failed']:
                if 'name' in item:
                    print(f"  - {item['name']}")
                    print(f"    URL: {item['url']}")
                    print(f"    Error: {item['error']}")
                else:
                    print(f"  - {item.get('entry', 'Unknown')}")
                    print(f"    Error: {item['error']}")
        
        print("=" * 60)
        
        if log_file:
            print(f"\nLog file saved to: {log_file}")


if __name__ == "__main__":
    main()