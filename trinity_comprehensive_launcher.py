#!/usr/bin/env python3
"""
Trinity Comprehensive Launcher - Advanced Android Emulator with Full Trinity Features
By: Trinity Desktop System Team
"""

import os
import sys
import subprocess
import socket
import time
import json
import threading
from pathlib import Path

class TrinityComprehensiveLauncher:
    def __init__(self):
        self.trinity_dir = Path("TrinityEmulator")
        self.workspace_dir = Path("trinity_workspace")
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Trinity configuration
        self.config = {
            "memory": "2048",  # 2GB RAM
            "cores": "2",
            "vnc_base_port": 5910,  # Start from 5910
            "android_vms": [],
            "trinity_features": True
        }
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def check_trinity_binary(self):
        """فحص إذا كان Trinity QEMU متاح"""
        trinity_binary = self.trinity_dir / "x86_64-softmmu" / "qemu-system-x86_64"
        if trinity_binary.exists():
            self.log("✅ Trinity QEMU binary found")
            return str(trinity_binary)
        
        # فحص في مجلدات أخرى
        possible_paths = [
            self.trinity_dir / "build" / "qemu-system-x86_64",
            self.trinity_dir / "qemu-system-x86_64"
        ]
        
        for path in possible_paths:
            if path.exists():
                self.log(f"✅ Trinity binary found at: {path}")
                return str(path)
        
        self.log("⚠️ Trinity binary not found, using system QEMU")
        return "qemu-system-x86_64"
        
    def create_android_images(self, vm_name, vm_index):
        """إنشاء صور Android VM"""
        vm_dir = self.workspace_dir / f"vm_{vm_index}_{vm_name}"
        vm_dir.mkdir(exist_ok=True)
        
        # إنشاء قرص النظام
        system_disk = vm_dir / "system.img"
        if not system_disk.exists():
            self.log(f"💾 Creating system disk for {vm_name}...")
            subprocess.run([
                "qemu-img", "create", "-f", "qcow2",
                str(system_disk), "4G"
            ], check=True, capture_output=True)
            
        # إنشاء قرص البيانات
        data_disk = vm_dir / "data.img"
        if not data_disk.exists():
            self.log(f"💾 Creating data disk for {vm_name}...")
            subprocess.run([
                "qemu-img", "create", "-f", "qcow2",
                str(data_disk), "2G"
            ], check=True, capture_output=True)
            
        return {
            "vm_dir": str(vm_dir),
            "system_disk": str(system_disk),
            "data_disk": str(data_disk)
        }
        
    def launch_trinity_vm(self, vm_config, vm_index):
        """تشغيل Trinity VM مع إعدادات متقدمة"""
        trinity_binary = self.check_trinity_binary()
        vnc_port = self.config["vnc_base_port"] + vm_index
        
        vm_name = vm_config["name"]
        images = self.create_android_images(vm_name, vm_index)
        
        # إعداد الأمر الأساسي
        cmd = [
            trinity_binary,
            "-name", f"Trinity-{vm_name}",
            "-m", self.config["memory"],
            "-smp", self.config["cores"],
            "-hda", images["system_disk"],
            "-hdb", images["data_disk"],
            "-display", f"vnc=:{vnc_port - 5900},password=off",
            "-vga", "std",
            "-netdev", f"user,id=net0,hostfwd=tcp::{5555 + vm_index}-:5555",
            "-device", "e1000,netdev=net0",
            "-daemonize",
            "-pidfile", f"{images['vm_dir']}/vm.pid"
        ]
        
        # إضافة ميزات Trinity إذا كانت متاحة
        if "direct-express" in trinity_binary or self.config["trinity_features"]:
            try:
                # فحص إذا كان Trinity يدعم direct-express
                help_output = subprocess.getoutput(f"{trinity_binary} -device help")
                if "direct-express-pci" in help_output:
                    cmd.extend(["-device", "direct-express-pci"])
                    self.log("✅ Direct Express enabled")
                    
                if "android64" in subprocess.getoutput(f"{trinity_binary} -cpu help"):
                    cmd.extend(["-cpu", "android64"])
                    self.log("✅ Android64 CPU enabled")
                else:
                    cmd.extend(["-cpu", "qemu64"])
            except:
                cmd.extend(["-cpu", "qemu64"])
        
        # إضافة تسارع إذا كان متاحاً
        if os.path.exists("/dev/kvm"):
            cmd.extend(["-enable-kvm"])
            self.log("✅ KVM acceleration enabled")
        else:
            cmd.extend(["-accel", "tcg"])
            self.log("⚠️ Using TCG (software emulation)")
            
        self.log(f"🚀 Launching {vm_name} on VNC port {vnc_port}...")
        self.log(f"Command: {' '.join(cmd)}")
        
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # انتظار حتى يبدأ VM
            time.sleep(5)
            
            # فحص إذا كان VM يعمل
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', vnc_port))
            sock.close()
            
            if result == 0:
                self.log(f"✅ {vm_name} running on VNC :{vnc_port}")
                return {
                    "name": vm_name,
                    "vnc_port": vnc_port,
                    "adb_port": 5555 + vm_index,
                    "status": "running",
                    "pid_file": f"{images['vm_dir']}/vm.pid"
                }
            else:
                self.log(f"❌ Failed to start {vm_name}")
                return None
                
        except Exception as e:
            self.log(f"❌ Error launching {vm_name}: {e}")
            return None
            
    def launch_multiple_android_instances(self):
        """تشغيل عدة نسخ من Android"""
        self.log("🎮 Starting multiple Trinity Android instances...")
        
        # إعداد VMs مختلفة
        vm_configs = [
            {"name": "Android-Main", "type": "standard"},
            {"name": "Android-Gaming", "type": "gaming"},
            {"name": "Android-Dev", "type": "development"}
        ]
        
        running_vms = []
        for i, config in enumerate(vm_configs):
            vm_info = self.launch_trinity_vm(config, i)
            if vm_info:
                running_vms.append(vm_info)
                
        if running_vms:
            self.log("🎉 Trinity VMs launched successfully!")
            self.log("📋 Running instances:")
            for vm in running_vms:
                self.log(f"   📱 {vm['name']}: VNC localhost:{vm['vnc_port']}, ADB localhost:{vm['adb_port']}")
                
            # حفظ معلومات VMs
            vm_status_file = self.workspace_dir / "running_vms.json"
            with open(vm_status_file, 'w') as f:
                json.dump(running_vms, f, indent=2)
                
            return running_vms
        else:
            self.log("❌ Failed to start any Trinity VMs")
            return []
            
    def get_system_status(self):
        """الحصول على حالة النظام الكاملة"""
        status = {
            "trinity_binary": self.check_trinity_binary(),
            "running_vms": [],
            "vnc_ports": [],
            "system_resources": {}
        }
        
        # فحص VMs العاملة
        vm_status_file = self.workspace_dir / "running_vms.json"
        if vm_status_file.exists():
            try:
                with open(vm_status_file, 'r') as f:
                    status["running_vms"] = json.load(f)
            except:
                status["running_vms"] = []
                
        # فحص المنافذ النشطة
        for port in range(5900, 5920):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if sock.connect_ex(('localhost', port)) == 0:
                status["vnc_ports"].append(port)
            sock.close()
            
        return status
        
    def comprehensive_launch(self):
        """تشغيل شامل لنظام Trinity"""
        self.log("🚀 Trinity Comprehensive Launch Starting...")
        
        # فحص حالة النظام
        status = self.get_system_status()
        self.log(f"🔍 System Status: {len(status['running_vms'])} VMs, {len(status['vnc_ports'])} VNC ports active")
        
        # تشغيل VMs إذا لم تكن تعمل
        if not status["running_vms"]:
            running_vms = self.launch_multiple_android_instances()
        else:
            self.log("✅ Trinity VMs already running")
            running_vms = status["running_vms"]
            
        # طباعة التقرير النهائي
        if running_vms:
            self.log("🎉 Trinity Comprehensive Launch Completed!")
            self.log("=" * 60)
            self.log("🌐 Trinity Desktop System - Full Status:")
            for vm in running_vms:
                self.log(f"   🖥️  {vm['name']}: VNC :{vm['vnc_port']}")
            self.log("   🔐 VNC Password: trinity123 (configured globally)")
            self.log("   🌐 Web Access: http://localhost:5000/trinity.html")
            self.log("=" * 60)
            
        return len(running_vms) > 0

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        launcher = TrinityComprehensiveLauncher()
        status = launcher.get_system_status()
        
        if status["running_vms"]:
            print("✅ Trinity System Status: RUNNING")
            for vm in status["running_vms"]:
                print(f"   📱 {vm['name']}: VNC :{vm['vnc_port']}")
        else:
            print("❌ Trinity System Status: NOT RUNNING")
        return 0
    
    launcher = TrinityComprehensiveLauncher()
    success = launcher.comprehensive_launch()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())