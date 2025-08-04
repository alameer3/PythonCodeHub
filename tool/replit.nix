{ pkgs }: {
  deps = [
    pkgs.x11vnc
    pkgs.xorg.xorgserver
    pkgs.xorg.xrandr
    pkgs.xorg.xauth
    pkgs.lxde
    pkgs.chromium  # بدل Firefox
    pkgs.wget
    pkgs.git
    pkgs.python3
    pkgs.curl
    pkgs.netcat
    pkgs.unzip
  ];
}