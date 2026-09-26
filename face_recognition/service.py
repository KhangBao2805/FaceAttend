"""
FaceRecognitionService — lớp TÁCH BIỆT xử lý nhận diện khuôn mặt.

Mục đích:
- Phần giao diện (templates/static) và database (app.py) KHÔNG gọi
  trực tiếp thư viện face_recognition.
- Mọi thao tác khuôn mặt đi qua class này.
- Sau này muốn dùng dlib / face_recognition / InsightFace / API cloud
  chỉ cần sửa file này, không sửa toàn bộ project.

Chế độ hiện tại: MOCK (giả lập) để chạy ngay trên Windows mà không cần
cài dlib (dlib rất hay lỗi trên Windows).
- embedding: vector 128 số thực, lưu dạng JSON trong bảng face_data.
- Frontend tạo embedding giả lập từ camera (demo) hoặc gửi embedding thật.
- recognize(): so khoảng cách Euclid với dữ liệu đã lưu.

Bảo mật:
- Không bao giờ lưu ảnh thô lên server ở bản mock này.
- Chỉ lưu vector embedding + cờ consent (đồng ý).
"""

import json
import math
import sqlite3
from datetime import datetime

DB_PATH = "database.db"  # đường dẫn tương đối, app.py sẽ ghi đè bằng absolute path


class FaceRecognitionService:
    """Dịch vụ nhận diện khuôn mặt (bản giả lập, dễ thay thế)."""

    # Ngưỡng khoảng cách: càng nhỏ càng chặt. Mock dùng 0.6
    THRESHOLD = 0.6

    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        # Thử nạp thư viện thật (nếu máy cài được). Không bắt buộc.
        self._real_lib = None
        try:
            import face_recognition  # type: ignore
            self._real_lib = face_recognition
        except Exception:
            self._real_lib = None  # chạy mock, vẫn OK

    # ---------- tiện ích nội bộ ----------
    def _conn(self):
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        return c

    @staticmethod
    def _distance(a, b):
        """Khoảng cách Euclid giữa 2 vector."""
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    # ---------- API chính ----------
    def register(self, student_code, embedding, consent=False):
        """Đăng ký / cập nhật vector khuôn mặt cho 1 học sinh."""
        if not consent:
            return {"ok": False, "msg": "Cần có sự đồng ý (consent) trước khi lưu dữ liệu khuôn mặt."}
        if not embedding or len(embedding) < 16:
            return {"ok": False, "msg": "Dữ liệu khuôn mặt không hợp lệ."}
        c = self._conn()
        c.execute(
            """INSERT INTO face_data(student_code, embedding, consent, created_at)
               VALUES(?,?,?,?)
               ON CONFLICT(student_code) DO UPDATE SET
                 embedding=excluded.embedding, consent=excluded.consent,
                 created_at=excluded.created_at""",
            (student_code, json.dumps(embedding), 1 if consent else 0,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        c.execute("UPDATE students SET face_registered=1 WHERE code=?", (student_code,))
        c.commit()
        c.close()
        return {"ok": True, "msg": "Đăng ký khuôn mặt thành công."}

    def recognize(self, embedding):
        """Nhận diện 1 embedding -> mã học sinh gần nhất (hoặc None)."""
        if not embedding:
            return {"ok": False, "msg": "Thiếu dữ liệu khuôn mặt."}
        c = self._conn()
        rows = c.execute("SELECT student_code, embedding FROM face_data").fetchall()
        c.close()
        best, best_d = None, 1e9
        for r in rows:
            try:
                known = json.loads(r["embedding"])
            except Exception:
                continue
            if len(known) != len(embedding):
                continue
            d = self._distance(known, embedding)
            if d < best_d:
                best_d, best = d, r["student_code"]
        if best and best_d <= self.THRESHOLD:
            return {"ok": True, "student_code": best,
                    "distance": round(best_d, 4), "engine": "mock"}
        return {"ok": False, "msg": "Không nhận diện được.", "engine": "mock"}

    def delete(self, student_code):
        """Xóa dữ liệu khuôn mặt (quyền riêng tư: người dùng được yêu cầu xóa)."""
        c = self._conn()
        c.execute("DELETE FROM face_data WHERE student_code=?", (student_code,))
        c.execute("UPDATE students SET face_registered=0 WHERE code=?", (student_code,))
        c.commit()
        c.close()
        return {"ok": True}

    # ---------- Mở rộng tương lai ----------
    # def register_from_image(self, image_bytes): ...
    #   -> dùng self._real_lib.face_encodings(...) rồi gọi self.register(...)
    # def recognize_from_image(self, image_bytes): ...
