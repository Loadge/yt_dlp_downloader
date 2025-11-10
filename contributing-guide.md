# Contributing to YouTube Downloader

Thank you for your interest in contributing to this project! We welcome contributions from everyone.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Python version, Docker version if applicable)
- Relevant logs or error messages
- Sample YAML config (remove any sensitive URLs)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:
- A clear description of the enhancement
- Use cases and benefits
- Possible implementation approach (optional)

### Pull Requests

1. **Fork the repository** and create your branch from `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes**:
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

3. **Test your changes**:
   ```bash
   # Test the Python script
   python youtube_downloader.py examples/basic.yaml
   
   # Test Docker build
   docker build -t yt-downloader-test .
   docker run --rm -v $(pwd)/config:/config:ro -v $(pwd)/downloads:/downloads yt-downloader-test
   ```

4. **Update documentation**:
   - Update README.md if you're adding features
   - Add examples if relevant
   - Update DOCKER.md for Docker-related changes

5. **Commit your changes**:
   ```bash
   git commit -m "Add: Brief description of your changes"
   ```
   
   Use conventional commit messages:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Docs:` for documentation changes
   - `Refactor:` for code refactoring

6. **Push to your fork**:
   ```bash
   git push origin feature/my-new-feature
   ```

7. **Create a Pull Request**:
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure all CI checks pass

## Development Setup

### Local Development

```bash
# Clone your fork
git clone https://github.com/yourusername/yt-dlp-downloader.git
cd yt-dlp-downloader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (if not already installed)
# Windows: winget install FFmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

### Docker Development

```bash
# Build test image
docker build -t yt-downloader-dev .

# Run tests
docker run --rm yt-downloader-dev python -c "import yt_dlp; import yaml; print('OK')"

# Test with example config
docker run --rm \
  -v $(pwd)/examples:/config:ro \
  -v $(pwd)/test_downloads:/downloads \
  yt-downloader-dev
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions
- Keep functions focused and concise
- Use type hints where appropriate

## Testing Checklist

Before submitting a PR, ensure:

- [ ] Code runs without errors
- [ ] Existing functionality still works
- [ ] New features have examples
- [ ] Documentation is updated
- [ ] Docker build succeeds
- [ ] No sensitive information in commits (URLs, tokens, etc.)

## Questions?

If you have questions about contributing, feel free to:
- Open an issue for discussion
- Comment on existing issues
- Check existing documentation

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow GitHub's community guidelines

Thank you for contributing! 🎉