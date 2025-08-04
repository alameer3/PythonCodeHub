# Desktop VNC System - Configuration Guide

## System Overview
This is a complete remote desktop VNC system running natively on Replit, migrated from Docker for better performance and compatibility.

## Service Configuration

### Core Services (8/8 Running)
1. **X Display Server**: Xvfb running on :1
2. **Desktop Environment**: Fluxbox window manager
3. **Web Browser**: Chromium with touch support
4. **VNC Server**: x11vnc on port 5900
5. **WebSocket Bridge**: websockify on port 5000
6. **HTTP Server**: Integrated with websockify
7. **noVNC Client**: Web-based VNC viewer
8. **CloudFlared**: Secure tunnel for external access

### Port Configuration
- **VNC Server**: 5900 (internal)
- **WebSocket/HTTP**: 5000 (main access port)
- **Replit compatibility**: Uses port 5000 for external access

### Authentication
- **VNC Password**: `123456`
- **Stored in**: `~/.vnc/passwd`

## Interface Options

### 1. Standard Interface (`/vnc.html`)
- Default noVNC interface
- Best for desktop computers
- Full feature set

### 2. Touch Interface (`/touch.html`)
- Optimized for mobile devices
- Touch gesture support
- Simplified controls
- Error-free JavaScript implementation

### 3. Advanced Mobile (`/mobile.html`)
- Advanced mobile features
- Custom touch controls
- Mobile-specific optimizations

### 4. Arabic Interface (`/arabic.html`)
- Full Arabic language support
- RTL (right-to-left) text direction
- Arabic labels and messages
- UTF-8 encoding for proper display
- Mobile-friendly design

## System Settings

### Touch Optimization
```json
{
    "view_only": false,
    "scale_viewport": true,
    "drag_viewport": true,
    "show_dot_cursor": false,
    "local_cursor": true,
    "touch_button": 1,
    "quality_level": 6,
    "compression_level": 2,
    "bell": false,
    "clipboard": true,
    "resize_session": false
}
```

### Mobile Features
- Touch gesture recognition
- Drag to navigate viewport
- Pinch to zoom support
- Virtual keyboard integration
- Fullscreen mode toggle

### Arabic Language Support
- UTF-8 character encoding
- RTL text direction
- Arabic font optimization
- Culturally appropriate UI elements
- Proper Arabic typography

## Package Dependencies

### System Packages (Nix)
- `xorg.xvfb` - Virtual display server
- `x11vnc` - VNC server
- `chromium` - Web browser
- `fluxbox` - Window manager
- `git` - Version control
- `python3` - Python runtime
- `unzip` - Archive utility

### Python Packages
- `websockify` - WebSocket to TCP bridge
- `numpy` - Mathematical operations

## CloudFlared Integration
- Automatic tunnel creation
- HTTPS encryption
- Dynamic URL generation
- External access without port forwarding

## Performance Optimization
- Quality level 6 for balanced performance
- Compression level 2 for speed
- Disabled unnecessary features (bell, dot cursor)
- Optimized for mobile bandwidth

## Troubleshooting

### Common Issues
1. **Arabic text not displaying**: Check UTF-8 encoding
2. **Touch not working**: Use touch.html or arabic.html interfaces  
3. **Connection timeout**: Verify port 5000 is accessible
4. **VNC password error**: Default password is "123456"

### Logs Location
- X11VNC: `/tmp/x11vnc.log`
- noVNC/websockify: `/tmp/novnc.log`
- CloudFlared: `/tmp/cloudflared.log`
- System: `/tmp/desktop.log`

## Access URLs
- **Local Standard**: `http://localhost:5000/vnc.html`
- **Local Touch**: `http://localhost:5000/touch.html`
- **Local Arabic**: `http://localhost:5000/arabic.html`
- **External**: Via CloudFlared tunnel (dynamic URL)

## Security Notes
- System runs in Replit sandbox environment
- VNC password should be changed for production use
- CloudFlared provides encrypted tunnel access
- No persistent storage of sensitive data

## Migration Notes
- Successfully migrated from Docker to native Replit
- All dependencies resolved for Replit environment
- Port configuration updated for Replit compatibility
- Websockify path issues resolved
- Arabic language support added post-migration