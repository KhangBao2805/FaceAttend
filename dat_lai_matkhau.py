# -*- coding: utf-8 -*-
"""Dat lai mat khau tai khoan Flask. Chay: py dat_lai_matkhau.py"""
import getpass
from werkzeug.security import generate_password_hash
from database.db import get_db

username = input("Ten dang nhap can reset: ").strip()
if not username:
    print("Thieu ten dang nhap.")
    raise SystemExit(1)
db = get_db()
u = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
if not u:
    print("Khong tim thay tai khoan:", username)
    db.close()
    raise SystemExit(1)
pw = getpass.getpass("Mat khau moi: ")
if not pw:
    print("Mat khau rong.")
    db.close()
    raise SystemExit(1)
db.execute("UPDATE users SET password_hash=? WHERE username=?",
           (generate_password_hash(pw), username))
db.commit()
db.close()
print("Da dat lai mat khau cho:", username)
