# FaceAttend — Điểm danh khuôn mặt cho THPT (SaaS)

Chạy: `py app.py` → http://127.0.0.1:5000 — Demo: `admin/admin123` · `gv_an/gv123` · `hs001/hs123`

## Kiến trúc (không dồn vào một file)
```
attendance-face/
  app.py            entry point mỏng (đăng ký blueprint + init DB)
  config.py         cấu hình tập trung
  database/         db.py (kết nối) · schema.sql · seed.py (30 HS, 30 ngày công)
  auth/             routes.py (login/logout) · decorators.py (phân quyền)
  routes/           pages.py (render khung HTML)
  api/              core.py (HS + lớp) · attendance.py (điểm danh + face + TKB) · misc.py (dashboard/thống kê/thông báo/tài khoản)
  services/         face_service.py · attendance_service.py · stats_service.py
  face_recognition/ module cũ (giữ tương thích) — logic chuẩn ở services/face_service.py
  templates/        layouts/base.html · pages/*.html
  static/           css/design.css (design system) · js/app.js (api/theme/toast/modal/avatar/camera)
```

## Face Recognition (module riêng)
`services/face_service.py` — `FaceRecognitionService` với `registerFace / detectFace / recognizeFace / verifyFace / deleteFace`.
Bản MOCK để demo chạy ngay; thay bằng model thật chỉ cần sửa file này.
Frontend gọi qua `/api/face/*`, không bao giờ chạm trực tiếp model. Không lưu ảnh công khai, không lưu gì ở localStorage.

## Tính năng
Dashboard (4 KPI + % so với hôm qua, line 7/30 ngày, donut rate, cột theo lớp, recent) ·
Điểm danh (camera + overlay + scan, card kết quả, chống trùng ngày+tiết+môn) ·
Học sinh (tìm/lọc, CRUD, profile + biểu đồ) · Đăng ký khuôn mặt 3 bước (consent bắt buộc) ·
Lớp học (cards + chi tiết) · TKB lưới T2–T7 · Lịch sử (lọc date-range, xuất CSV + Excel) ·
Thống kê (range, top đi trễ) · Thông báo (bell + unread) · Tài khoản · Cài đặt giờ tiết ·
Dark mode, responsive (sidebar drawer + bottom nav mobile), skeleton/empty/toast/modal.
