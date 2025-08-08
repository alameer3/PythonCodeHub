#!/bin/bash

# Trinity Builder Script - Linux Compatible Version
# By: Trinity Desktop System

set -e  # Exit on any error

echo "🔧 Building Trinity Emulator for Linux..."

# Navigate to Trinity directory
cd TrinityEmulator

# Fix line endings in all critical files
echo "🔄 Fixing line endings..."
find . -name "configure" -exec sed -i 's/\r$//' {} \;
find . -name "*.sh" -exec sed -i 's/\r$//' {} \;
find . -name "Makefile*" -exec sed -i 's/\r$//' {} \;

# Make configure executable
chmod +x configure

# Set up build environment for Linux
export CC=gcc
export CXX=g++
export CFLAGS="-O2 -g -fPIC"
export CXXFLAGS="-O2 -g -fPIC"
export LDFLAGS="-Wl,--as-needed"

# Configure Trinity with Linux-compatible options (no SDL dependency)
echo "🔧 Configuring Trinity..."
./configure \
    --enable-kvm \
    --disable-sdl \
    --disable-gtk \
    --target-list=x86_64-softmmu \
    --disable-werror \
    --enable-vnc \
    --disable-xen \
    --disable-spice \
    --enable-tcg \
    --disable-capstone \
    --disable-smartcard \
    --disable-nettle \
    --prefix=/tmp/trinity-build \
    --disable-virtfs \
    --disable-docs \
    --disable-curl \
    --disable-bluez \
    --disable-brlapi \
    --audio-drv-list="" \
    2>&1 | tee configure.log

# Build Trinity
echo "🔨 Building Trinity (this may take some time)..."
make -j2 2>&1 | tee build.log

echo "✅ Trinity build completed!"

# Check if the binary was built
if [ -f "x86_64-softmmu/qemu-system-x86_64" ]; then
    echo "✅ Trinity binary created: x86_64-softmmu/qemu-system-x86_64"
    ls -la x86_64-softmmu/qemu-system-x86_64
else
    echo "❌ Trinity binary not found"
    exit 1
fi

echo "🎉 Trinity build successful!"