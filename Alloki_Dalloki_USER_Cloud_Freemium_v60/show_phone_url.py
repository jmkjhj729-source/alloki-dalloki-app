#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket

def get_ips():
    ips = set()
    hostname = socket.gethostname()
    try:
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ":" not in ip and not ip.startswith("127."):
                ips.add(ip)
    except Exception:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ips.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    return sorted(ips)

if __name__ == "__main__":
    ips = get_ips()
    if not ips:
        print("IP not found. Run `ipconfig` (Windows) or `ifconfig`/`ip a` (Mac/Linux).")
    else:
        print("Open on your phone (same Wi‑Fi):")
        for ip in ips:
            print(f"  http://{ip}:8501")
