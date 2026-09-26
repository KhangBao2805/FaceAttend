# -*- coding: utf-8 -*-
"""Tạo tài khoản Admin thật. Chạy: py tao_admin.py (làm theo hướng dẫn)."""
import getpass
from datetime import datetime
from werkzeug.security import generate_password_hash
from database.db import get_db

username = input("Tên đăng nhập: ").strip()
full_name = input("Họ tên: ").strip() or username
password = getpass.getpass("Mật khẩu: ")
if not username or not password:
    print("Thiếu tên đăng nhập hoặc mật khẩu.")
    raise SystemExit(1)
db = get_db()
try:
    db.execute("INSERT INTO users(username,password_hash,role,full_name,created_at) VALUES(?,?,?,?,?)",
               (username, generate_password_hash(password), "admin", full_name,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    db.commit()
    print(f"Đã tạo Admin '{username}'. Đăng nhập tại http://127.0.0.1:5000/login")
except Exception as e:
    print("Lỗi:", e)
finally:
    db.close()
