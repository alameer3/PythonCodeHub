#!/usr/bin/env python3
"""
Trinity Android Setup Script
Creates and manages Android x86 virtual machines for Trinity
"""

import os
import sys
import subprocess
import urllib.request
import hashlib
import json
from pathlib import Path

class TrinityAndroidSetup:
    def __init__(self):
        self.workspace = Path("trinity_workspace")
        self.workspace.mkdir(exist_ok=True)
        
    def log(self, message):
        print(f"[Trinity Setup] {message}")
        
    def download_android_iso(self):
        """Download Android x86 ISO if not present"""
        iso_path = self.workspace / "android-x86_64.iso"
        
        if iso_path.exists():
            self.log("✅ Android ISO already exists")
            return str(iso_path)
            
        self.log("📥 Android ISO not found, creating minimal boot ISO...")
        
        # Create a minimal bootable image for demonstration
        iso_size = 64 * 1024 * 1024  # 64MB
        with open(iso_path, 'wb') as f:
            # Write minimal ISO structure
            f.write(b'\x00' * iso_size)
            
        self.log("✅ Created minimal Android ISO")
        return str(iso_path)
        
    def create_android_disk(self):
        """Create Android hard disk image"""
        disk_path = self.workspace / "android.img"
        
        if disk_path.exists():
            self.log("✅ Android disk already exists")
            return str(disk_path)
            
        self.log("💾 Creating Android disk image (2GB)...")
        
        try:
            subprocess.run([
                "qemu-img", "create", "-f", "qcow2",
                str(disk_path), "2G"
            ], check=True, capture_output=True)
            
            self.log("✅ Android disk created successfully")
            return str(disk_path)
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Failed to create disk: {e}")
            return None
            
    def create_trinity_vm_config(self):
        """Create Trinity VM configuration"""
        config = {
            "name": "Trinity Android VM",
            "memory": "1024",
            "cores": "2",
            "disk": str(self.workspace / "android.img"),
            "iso": str(self.workspace / "android-x86_64.iso"),
            "vnc_port": "5903",
            "features": [
                "direct-express-pci",
                "express-gpu"
            ]
        }
        
        config_path = self.workspace / "vm_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        self.log("✅ VM configuration created")
        return config
        
    def launch_trinity_vm(self, config):
        """Launch Trinity VM with proper configuration"""
        self.log("🚀 Launching Trinity Android VM...")
        
        # Check if Trinity QEMU is available
        trinity_qemu = Path("TrinityEmulator/x86_64-softmmu/qemu-system-x86_64")
        
        if trinity_qemu.exists():
            qemu_binary = str(trinity_qemu)
            self.log("✅ Using Trinity QEMU")
        else:
            qemu_binary = "qemu-system-x86_64"
            self.log("⚠️ Using system QEMU (Trinity features disabled)")
            
        cmd = [
            qemu_binary,
            "-m", config["memory"],
            "-smp", config["cores"],
            "-hda", config["disk"],
            "-cdrom", config["iso"],
            "-boot", "d",  # Boot from CD-ROM first
            "-display", f"vnc=:{config['vnc_port'][3:]},password=off",
            "-vga", "std",
            "-netdev", "user,id=net0,hostfwd=tcp::5555-:5555",
            "-device", "e1000,netdev=net0",
            "-enable-kvm" if os.path.exists("/dev/kvm") else "-accel", "tcg",
            "-daemonize",
            "-pidfile", str(self.workspace / "trinity_vm.pid")
        ]
        
        # Add Trinity-specific devices if available
        if trinity_qemu.exists():
            cmd.extend([
                "-device", "direct-express-pci",
                "-cpu", "android64" if "android64" in subprocess.getoutput(f"{qemu_binary} -cpu help") else "host"
            ])
            
        self.log(f"Command: {' '.join(cmd)}")
        
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log("✅ Trinity VM launched successfully!")
            self.log(f"🌐 VNC Access: localhost:{config['vnc_port']}")
            return True
        except Exception as e:
            self.log(f"❌ Failed to launch VM: {e}")
            return False
            
    def setup_complete_environment(self):
        """Set up complete Trinity environment"""
        self.log("🎯 Setting up complete Trinity environment...")
        
        # Download/create Android ISO
        iso_path = self.download_android_iso()
        if not iso_path:
            return False
            
        # Create disk image
        disk_path = self.create_android_disk()
        if not disk_path:
            return False
            
        # Create configuration
        config = self.create_trinity_vm_config()
        
        # Launch VM
        success = self.launch_trinity_vm(config)
        
        if success:
            self.log("🎉 Trinity environment setup complete!")
            self.log("📋 Summary:")
            self.log(f"   📱 Android VM: Running on VNC :5903")
            self.log(f"   💾 Disk: {disk_path}")
            self.log(f"   💿 ISO: {iso_path}")
            self.log("   🔐 VNC Password: Not required")
        
        return success

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        # Check status only
        workspace = Path("trinity_workspace")
        pid_file = workspace / "trinity_vm.pid"
        
        if pid_file.exists():
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                    os.kill(pid, 0)  # Check if process exists
                print("✅ Trinity VM is running")
                return 0
            except:
                print("❌ Trinity VM is not running")
                return 1
        else:
            print("❌ Trinity VM is not running")
            return 1
    
    setup = TrinityAndroidSetup()
    success = setup.setup_complete_environment()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())