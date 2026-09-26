# -*- coding: utf-8 -*-
"""FaceRecognitionService — module nhận diện khuôn mặt TÁCH BIỆT khỏi UI/DB.

API chuẩn (dùng cho mọi nơi):
  registerFace(student_code, embedding, consent) -> dict
  detectFace(image_meta)  -> dict  (mock: kiểm tra có khuôn mặt từ camera meta)
  recognizeFace(embedding) -> dict (so khớp Euclid với face_profiles + face_data cũ)
  verifyFace(student_code, embedding) -> dict (1:1, chống điểm danh hộ)
  deleteFace(student_code)

Bản MOCK chạy ngay trên Windows. Muốn dùng model thật (dlib/InsightFace/API),
chỉ sửa file này.
"""
import json
import math
from datetime import datetime
from database.db import get_db

THRESHOLD = 0.6


def _distance(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _known_faces():
    """Đọc cả bảng mới face_profiles và bảng cũ face_data (tương thích)."""
    db = get_db()
    rows = []
    for tbl in ("face_profiles", "face_data"):
        try:
            rows += [(r["student_code"], r["embedding"]) for r in
                     db.execute(f"SELECT student_code, embedding FROM {tbl}").fetchall()]
        except Exception:
            pass
    db.close()
    seen = {}
    for code, emb in rows:
        seen.setdefault(code, emb)
    return seen


class FaceRecognitionService:
    THRESHOLD = THRESHOLD

    # ---- API chuẩn ----
    def registerFace(self, student_code, embedding, consent=False):
        if not consent:
            return {"ok": False, "msg": "Cần sự đồng ý trước khi lưu dữ liệu khuôn mặt."}
        if not embedding or len(embedding) < 16:
            return {"ok": False, "msg": "Dữ liệu khuôn mặt không hợp lệ."}
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db = get_db()
        db.execute("""INSERT INTO face_profiles(student_code,embedding,consent,created_at)
                      VALUES(?,?,?,?) ON CONFLICT(student_code) DO UPDATE SET
                      embedding=excluded.embedding, consent=excluded.consent, created_at=excluded.created_at""",
                   (student_code, json.dumps(embedding), 1, now))
        db.execute("UPDATE students SET face_registered=1 WHERE code=?", (student_code,))
        db.commit()
        db.close()
        return {"ok": True, "msg": "Đăng ký khuôn mặt thành công."}

    def detectFace(self, image_meta=None):
        """Mock detect: client gửi {hasFace, blur, brightness}; trả về chất lượng."""
        m = image_meta or {}
        if not m.get("hasFace", True):
            return {"ok": False, "msg": "Không tìm thấy khuôn mặt trong khung."}
        return {"ok": True, "box": [0.3, 0.25, 0.4, 0.5], "quality": "good"}

    def recognizeFace(self, embedding):
        if not embedding:
            return {"ok": False, "msg": "Thiếu dữ liệu khuôn mặt."}
        best, best_d = None, 1e9
        for code, raw in _known_faces().items():
            try:
                known = json.loads(raw)
            except Exception:
                continue
            if len(known) != len(embedding):
                continue
            d = _distance(known, embedding)
            if d < best_d:
                best_d, best = d, code
        if best and best_d <= self.THRESHOLD:
            return {"ok": True, "student_code": best, "distance": round(best_d, 4), "engine": "mock"}
        return {"ok": False, "msg": "Không tìm thấy học sinh.", "engine": "mock"}

    def verifyFace(self, student_code, embedding):
        """Xác thực 1:1 — dùng khi nghi điểm danh hộ."""
        r = self.recognizeFace(embedding)
        if r.get("ok") and r.get("student_code") == student_code:
            return {"ok": True, "msg": "Xác thực đúng người."}
        return {"ok": False, "msg": "Khuôn mặt không khớp học sinh này."}

    def deleteFace(self, student_code):
        db = get_db()
        for tbl in ("face_profiles", "face_data"):
            try:
                db.execute(f"DELETE FROM {tbl} WHERE student_code=?", (student_code,))
            except Exception:
                pass
        db.execute("UPDATE students SET face_registered=0 WHERE code=?", (student_code,))
        db.commit()
        db.close()
        return {"ok": True}

    # ---- Alias tương thích code cũ ----
    register = registerFace
    recognize = recognizeFace
    delete = deleteFace


face_service = FaceRecognitionService()
