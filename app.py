# -*- coding: utf-8 -*-
"""FaceAttend — entry point (mỏng). Mọi logic nằm ở auth/ api/ routes/ services/ database/.

Chạy:  py app.py  ->  http://127.0.0.1:5000
Demo: admin/admin123 | gv_an/gv123 | hs001/hs123
"""
from datetime import timedelta
from flask import Flask
import os
import config
from database.db import get_db, init_schema

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.permanent_session_lifetime = timedelta(days=7)

# Blueprints: auth (login) / pages (HTML) / api (JSON)
from auth.routes import bp as auth_bp
from routes.pages import bp as pages_bp
from api.core import bp as core_bp
from api.attendance import bp as att_bp
from api.misc import bp as misc_bp

app.register_blueprint(auth_bp)
app.register_blueprint(pages_bp)
app.register_blueprint(core_bp)
app.register_blueprint(att_bp)
app.register_blueprint(misc_bp)


def _migrate_columns(db):
    """Thêm cột mới cho DB cũ (bỏ qua nếu đã có)."""
    alters = [
        "ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''",
        "ALTER TABLE users ADD COLUMN avatar_color TEXT DEFAULT ''",
        "ALTER TABLE students ADD COLUMN grade TEXT DEFAULT '12'",
        "ALTER TABLE students ADD COLUMN email TEXT DEFAULT ''",
        "ALTER TABLE students ADD COLUMN parent_phone TEXT DEFAULT ''",
        "ALTER TABLE students ADD COLUMN enroll_date TEXT DEFAULT ''",
        "ALTER TABLE classes ADD COLUMN grade TEXT DEFAULT '12'",
        "ALTER TABLE classes ADD COLUMN room TEXT DEFAULT ''",
        "ALTER TABLE classes ADD COLUMN capacity INTEGER DEFAULT 45",
        "ALTER TABLE subjects ADD COLUMN color TEXT DEFAULT ''",
        "ALTER TABLE schedules ADD COLUMN class_name TEXT DEFAULT '12A1'",
        "ALTER TABLE attendance ADD COLUMN class_name TEXT DEFAULT ''",
        "ALTER TABLE students ADD COLUMN photo TEXT DEFAULT ''",
    ]
    for sql in alters:
        try:
            db.execute(sql)
        except Exception:
            pass
    db.commit()


def init_db():
    init_schema()
    db = get_db()
    _migrate_columns(db)
    # File .noseed = đã xóa dữ liệu demo, không nạp lại khi khởi động
    if os.path.exists(os.path.join(config.BASE_DIR, ".noseed")):
        db.close()
        return
    n = db.execute("SELECT COUNT(*) c FROM students").fetchone()["c"]
    db.close()
    from database.seed import seed
    db = get_db()
    if n == 0:
        seed(db)
    elif n < 30:
        # Nâng demo cũ (20 HS) lên chuẩn mới (30 HS + 30 ngày lịch sử):
        db.execute("DELETE FROM attendance WHERE method='demo'")
        db.execute("DELETE FROM schedules")
        db.execute("DELETE FROM notifications")
        seed(db)
    db.close()


if __name__ == "__main__":
    init_db()
    print("=" * 55)
    print("  FaceAttend — http://127.0.0.1:5000")
    print("  admin/admin123 | gv_an/gv123 | hs001/hs123")
    print("=" * 55)
    app.run(debug=True)
