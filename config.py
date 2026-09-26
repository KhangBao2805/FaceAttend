"""Cấu hình tập trung cho FaceAttend."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
SECRET_KEY = os.environ.get("FACEATTEND_SECRET", "faceattend-saas-2026-change-me")
SCHOOL_NAME = "Trường THPT Nguyễn Du - Ninh Sơn"
APP_NAME = "FaceAttend"

# Quy tắc trạng thái: check-in trễ quá N phút thì tính "Đi trễ"
LATE_AFTER_MINUTES = 5
