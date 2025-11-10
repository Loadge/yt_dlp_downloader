# Network Drives Setup Guide for Docker

This guide explains how to download videos directly to network storage (NAS, file servers) using Docker on Windows.

## Why Map Network Drives?

Docker on Windows cannot directly mount UNC paths like `\\ServerName\ShareName`. You must first map the network location to a drive letter (Z:, Y:, X:, etc.) in Windows, then mount that drive in Docker.

## Step-by-Step Guide

### 1. Map Your Network Drive in Windows

#### Method A: Using File Explorer (GUI)

1. Open **File Explorer**
2. Click on **"This PC"** in the left sidebar
3. Click **"Map network drive"** in the toolbar (or right-click "This PC" → "Map network drive")
4. **Choose a drive letter** from the dropdown (e.g., Z:, Y:, X:)
5. **Enter the network path:**
   - Format: `\\ServerName\ShareName\Folder`
   - Example: `\\NAS_1\data`
   - Example: `\\192.168.1.100\Media`
6. **Optional but recommended:**
   - ✅ Check "Reconnect at sign-in" (drive will be available after restart)
   - ✅ Check "Connect using different credentials" (if needed)
7. Click **"Finish"**
8. Enter credentials if prompted

#### Method B: Using Command Line

Open **Command Prompt** or **PowerShell** as Administrator:

```cmd
# Basic mapping
net use Z: \\ServerName\ShareName

# With credentials
net use Z: \\ServerName\ShareName /user:username password

# Persistent mapping (reconnect at login)
net use Z: \\ServerName\ShareName /persistent:yes

# Map with prompt for credentials
net use Z: \\ServerName\ShareName /user:username *
```

**Examples:**
```cmd
# Map NAS to Z:
net use Z: \\NAS_1\data /persistent:yes

# Map file server to Y:
net use Y: \\FileServer\Media /persistent:yes

# Map with IP address
net use X: \\192.168.1.100\Backup /persistent:yes
```

#### Verify the Mapping

Open File Explorer and check that your drive appears under "This PC" with the assigned letter.

### 2. Configure docker-compose.yml

Edit your `docker-compose.yml` file and update the volumes section:

```yaml
services:
  yt-downloader:
    volumes:
      - ./config:/config:ro
      
      # Replace ./downloads with your mapped drive
      - Z:\03 Peliculas, Libros, Series\00 PELIS:/downloads
      
      - ./logs:/logs
```

**More examples:**

```yaml
# Download to root of Z: drive
- Z:\:/downloads

# Download to subfolder in Y: drive
- Y:\Media\YouTube:/downloads

# Download to specific folder in X: drive
- X:\Backup\Videos\YouTube:/downloads
```

### 3. Update Your videos.yaml Config

In your `config/videos.yaml`, use the **container path** (not the Windows path):

```yaml
target_folder: "/downloads"

videos:
  - url: "https://www.youtube.com/watch?v=example"
    name: "My Video"
```

**Important:** Always use `/downloads` in your YAML config, regardless of which Windows drive you mounted.

### 4. Run Docker Compose

```bash
docker-compose up
```

Videos will now download directly to your network drive!

## Common Scenarios

### Scenario 1: NAS with Shared Folders

**Your NAS:** `\\NAS_1\data\Videos`

```bash
# Map the drive
net use Z: \\NAS_1\data /persistent:yes
```

```yaml
# docker-compose.yml
volumes:
  - Z:\Videos:/downloads
```

```yaml
# videos.yaml
target_folder: "/downloads"
```

### Scenario 2: File Server with Multiple Shares

**File Server:** `\\FileServer\Media` and `\\FileServer\Backup`

```bash
# Map both shares
net use Y: \\FileServer\Media /persistent:yes
net use X: \\FileServer\Backup /persistent:yes
```

```yaml
# docker-compose.yml - Use Y: for main downloads
volumes:
  - Y:\YouTube:/downloads
```

### Scenario 3: Mix Local and Network Storage

```yaml
# docker-compose.yml
volumes:
  - ./config:/config:ro
  - Z:\NetworkVideos:/downloads  # Network storage for videos
  - ./logs:/logs                  # Local logs
```

## Troubleshooting

### Problem: "The network path was not found"

**Cause:** The network share is not accessible or mapped incorrectly.

**Solutions:**
1. Verify you can access the path in File Explorer
2. Check network connectivity to the server
3. Verify credentials are correct
4. Try accessing with IP instead of name: `\\192.168.1.100\share`

### Problem: Drive not persistent after restart

**Cause:** Drive not set to reconnect at sign-in.

**Solution:**
```cmd
net use Z: /delete
net use Z: \\ServerName\ShareName /persistent:yes
```

### Problem: "Access denied" when Docker tries to write

**Cause:** Insufficient permissions on the network share.

**Solutions:**
1. Verify your Windows user has write permissions on the network share
2. Map the drive with credentials that have write access:
   ```cmd
   net use Z: \\ServerName\ShareName /user:username password
   ```
3. Check folder permissions on the NAS/server

### Problem: Docker shows "/downloads" but writes to wrong location

**Cause:** Volume mount not configured correctly.

**Solution:**
1. Stop Docker: `docker-compose down`
2. Verify drive letter is correct in Windows
3. Update `docker-compose.yml` with correct drive path
4. Restart: `docker-compose up`

### Problem: Files download but can't be played

**Cause:** Possible corruption during network transfer.

**Solutions:**
1. Check network stability
2. Use wired connection instead of WiFi for large downloads
3. Check NAS/server disk space
4. Verify file system supports large files (avoid FAT32)

## Managing Mapped Drives

### List all mapped drives:
```cmd
net use
```

### Disconnect a mapped drive:
```cmd
net use Z: /delete
```

### Disconnect all drives:
```cmd
net use * /delete
```

### Reconnect drives after disconnect:
```cmd
net use Z: \\ServerName\ShareName /persistent:yes
```

## Best Practices

1. ✅ **Use persistent mappings** (`/persistent:yes`) so drives reconnect after restart
2. ✅ **Use descriptive drive letters** (Z: for main storage, Y: for backup, etc.)
3. ✅ **Test access before running Docker** - Open the drive in File Explorer first
4. ✅ **Use wired network** for large downloads when possible
5. ✅ **Keep credentials secure** - Consider using Windows Credential Manager
6. ✅ **Document your mappings** - Keep notes on what each drive letter represents

## Security Notes

- **Credentials in commands:** Be careful when using passwords in command line. They may appear in command history.
- **Credential Manager:** Windows stores credentials securely. Use `/savecred` option if needed.
- **Share permissions:** Ensure only necessary users have access to network shares.
- **Docker access:** Docker runs with your user's permissions, so it has the same access rights you do.

## Alternative: Using Local Storage with Manual Transfer

If network drives are problematic, consider:

1. Download to local machine: `- ./downloads:/downloads`
2. Run the downloader
3. Manually move files to network storage afterward

This approach is faster and more reliable for large downloads, though requires manual file management.

---

## Quick Reference

| Task | Command |
|------|---------|
| Map drive | `net use Z: \\Server\Share /persistent:yes` |
| List drives | `net use` |
| Remove drive | `net use Z: /delete` |
| Test access | Open drive in File Explorer |
| Verify in Docker | `docker-compose config` |

---

**Still having issues?** Check the main [DOCKER.md](DOCKER.md) documentation or open an issue on GitHub.