# Trinity Emulator Project

## Overview

Trinity is a high-performance Android emulator that utilizes graphics projection technology to achieve better compatibility, security, and efficiency compared to traditional emulators. The project includes both the main Trinity emulator and remote desktop client applications (bVNC, aRDP, aSPICE, and Opaque) for Android devices.

The emulator runs Android-x86 guest OS on Windows-x64 Intel machines with optional NVIDIA GPU acceleration. It supports both volatile "live boot" mode and persistent installation mode, providing a complete Android environment with Google Play Store access through OpenGApps integration.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Emulation Architecture
- **Host Platform**: Windows-x64 on Intel architecture with optional NVIDIA GPU support
- **Guest OS**: Android-x86 with OpenGApps integration
- **Virtualization Backend**: Intel HAXM or Windows Hyper-V for CPU virtualization
- **Graphics**: Novel graphics projection space technology for efficient rendering
- **Memory Management**: Supports memory over-commit without requiring full guest RAM pinning

### Remote Desktop Clients
- **Multi-Protocol Support**: VNC, RDP, SPICE, and oVirt/RHEV/Proxmox protocols
- **Cross-Platform**: Android applications with both free and pro versions
- **Backend Integration**: Supports hardware RDMA devices and Soft-RoCE (rxe) interfaces

### QEMU Integration
The project includes QEMU emulation components with:
- **COLO (COarse-grained LOck-stepping)**: High availability through primary/secondary VM replication
- **Advanced Features**: RDMA live migration, memory hotplug, throttling, and replay functionality
- **Block Device Management**: qcow2 format support with L2/refcount caching
- **Hardware Emulation**: Support for various device types including USB, PCI Express, audio, and network interfaces

### Storage and Memory
- **Volatile Mode**: 8GB storage limit, data erased on reboot
- **Persistent Mode**: Full installation with permanent storage
- **Memory Backend**: File-based and RAM-based backends with configurable caching
- **Hot-plug Support**: Runtime device addition/removal capabilities

### Network and Connectivity
- **ADB Integration**: Android Debug Bridge connectivity for development
- **Network Emulation**: Various network adapter emulations (e1000, virtio-net, etc.)
- **Remote Access**: Multiple remote desktop protocols for cross-platform access

## External Dependencies

### Hardware Requirements
- 4-core Intel CPU with VT support
- 8GB RAM minimum
- 128GB storage
- 1920x1080 display
- Optional: NVIDIA GPU with driver version 497.09+

### Software Dependencies
- **Windows Virtualization**: Intel HAXM v7.6.5 or Windows Hyper-V
- **Android Components**: Android-x86 guest OS with OpenGApps
- **Development Libraries**: NSS for cryptographic functions, librdmacm and libibverbs for RDMA support
- **Build Tools**: Standard development toolchain for QEMU compilation

### Third-Party Integrations
- **OpenGApps**: Google services integration for Android guest
- **NVIDIA Drivers**: Optional GPU acceleration support
- **Intel Technologies**: HAXM virtualization and VT support
- **Network Protocols**: SocketCAN for automotive applications, various remote desktop protocols
- **Storage Formats**: qcow2, raw images, and various block device backends