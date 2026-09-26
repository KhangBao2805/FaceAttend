# -*- coding: utf-8 -*-
"""Xóa TOÀN BỘ dữ liệu demo: users, students, attendance, face, notifications.
Giữ lại cấu hình: classes, subjects, periods, schedules.
Chạy: py xoa_demo.py — sau đó app sẽ KHÔNG tự nạp lại demo (nhờ file .noseed)."""
import os
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
db = sqlite3.connect(os.path.join(BASE, "database.db"))
for tbl in ("users", "students", "attendance", "face_profiles", "face_data", "notifications"):
    try:
        n = db.execute(f"DELETE FROM {tbl}").rowcount
        print(f"deleted {tbl}: {n} rows")
    except Exception as e:
        print(f"skip {tbl}: {e}")
db.commit()
db.close()
open(os.path.join(BASE, ".noseed"), "w").write("demo deleted")
print("Done. .noseed created - server will not re-seed demo.")
