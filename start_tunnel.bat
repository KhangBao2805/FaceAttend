@echo off
cd /d "C:\Users\Admin\Documents\Default Project\attendance-face"
cloudflared.exe tunnel --url http://127.0.0.1:5000
