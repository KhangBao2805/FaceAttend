# -*- coding: utf-8 -*-
"""Seed dữ liệu demo: 30 HS (12A1/12A2/12A3) + 30 ngày điểm danh + thông báo."""
import json
import random
from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash

PERIODS_DEFAULT = [
    (1, "Tiết 1", "07:00", "07:45", "Sáng"),
    (2, "Tiết 2", "07:50", "08:35", "Sáng"),
    (3, "Tiết 3", "08:40", "09:25", "Sáng"),
    (4, "Tiết 4", "09:40", "10:25", "Sáng"),
    (5, "Tiết 5", "10:30", "11:15", "Sáng"),
    (6, "Tiết 6", "13:30", "14:15", "Chiều"),
    (7, "Tiết 7", "14:20", "15:05", "Chiều"),
    (8, "Tiết 8", "15:10", "15:55", "Chiều"),
    (9, "Tiết 9", "16:00", "16:45", "Chiều"),
]

NAMES = ["Nguyễn Văn An", "Trần Văn Bình", "Lê Văn Cường", "Phạm Thị Dung",
         "Hoàng Văn Em", "Vũ Thị Phương", "Đặng Văn Giang", "Bùi Thị Hằng",
         "Đỗ Văn Hải", "Ngô Thị Lan", "Dương Văn Khoa", "Lý Thị Mai",
         "Trịnh Văn Nam", "Phan Thị Oanh", "Võ Văn Phúc", "Huỳnh Thị Quỳnh",
         "Trương Văn Rin", "Đinh Thị Sương", "Lê Văn Tùng", "Nguyễn Thị Uyên",
         "Trần Thị Vân", "Lê Văn Hoàng", "Phạm Văn Khải", "Hoàng Thị Linh",
         "Vũ Văn Minh", "Đặng Thị Ngọc", "Bùi Văn Phát", "Đỗ Thị Quyên",
         "Ngô Văn Sơn", "Dương Thị Thảo"]


def seed(db):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for p in PERIODS_DEFAULT:
        db.execute("INSERT OR IGNORE INTO periods(period,label,start_time,end_time,session) VALUES(?,?,?,?,?)", p)
    users = [
        ("admin", "admin@faceattend.edu.vn", generate_password_hash("admin123"), "admin", "Ban Giám Hiệu", None),
        ("gv_an", "an@faceattend.edu.vn", generate_password_hash("gv123"), "teacher", "Cô Nguyễn Thị An", None),
        ("hs001", "hs001@faceattend.edu.vn", generate_password_hash("hs123"), "student", NAMES[0], "HS001"),
    ]
    for u in users:
        db.execute("INSERT OR IGNORE INTO users(username,email,password_hash,role,full_name,linked_student_code,created_at) VALUES(?,?,?,?,?,?,?)",
                   (*u, now))
    for cl, grade, gvcn, room in [("12A1", "12", "Cô Nguyễn Thị An", "A201"),
                                  ("12A2", "12", "Thầy Trần Văn Đức", "A202"),
                                  ("12A3", "12", "Cô Lê Thu Hà", "A203")]:
        db.execute("INSERT OR IGNORE INTO classes(name,grade,homeroom,room) VALUES(?,?,?,?)", (cl, grade, gvcn, room))
    for code, name, color in [("TOAN", "Toán", "#2563eb"), ("VAN", "Ngữ Văn", "#7c3aed"),
                              ("ANH", "Tiếng Anh", "#0891b2"), ("LY", "Vật Lý", "#ea580c"),
                              ("HOA", "Hóa Học", "#16a34a"), ("TIN", "Tin Học", "#4f46e5")]:
        db.execute("INSERT OR IGNORE INTO subjects(code,name,color) VALUES(?,?,?)", (code, name, color))
    for t in [("GV01", "Cô Nguyễn Thị An", "Toán", "0901"), ("GV02", "Thầy Trần Văn Đức", "Vật Lý", "0902"),
              ("GV03", "Cô Lê Thu Hà", "Ngữ Văn", "0903"), ("GV04", "Thầy Phạm Minh Tuấn", "Tiếng Anh", "0904")]:
        db.execute("INSERT OR IGNORE INTO teachers(code,full_name,subject,phone) VALUES(?,?,?,?)", t)
    # 30 học sinh
    for i, nm in enumerate(NAMES, 1):
        code = f"HS{i:03d}"
        cl = "12A1" if i <= 10 else ("12A2" if i <= 20 else "12A3")
        db.execute("""INSERT OR IGNORE INTO students(code,full_name,class_name,grade,dob,gender,email,parent_phone,enroll_date,face_registered,created_at)
                      VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                   (code, nm, cl, "12", f"2008-{(i % 12) + 1:02d}-{(i % 27) + 1:02d}",
                    "Nam" if i % 2 else "Nữ", f"{code.lower()}@faceattend.edu.vn",
                    f"09{i:08d}", "2023-09-05", 1 if i <= 22 else 0, now))
        if i <= 22:
            emb = json.dumps([round(random.gauss(0, 1), 4) for _ in range(128)])
            db.execute("INSERT OR IGNORE INTO face_profiles(student_code,embedding,consent,created_at) VALUES(?,?,1,?)",
                       (code, emb, now))
    # Thời khóa biểu T2-T7
    subj_cycle = ["Toán", "Ngữ Văn", "Tiếng Anh", "Vật Lý", "Hóa Học", "Tin Học"]
    gv_map = {"Toán": "Cô Nguyễn Thị An", "Ngữ Văn": "Cô Lê Thu Hà", "Tiếng Anh": "Thầy Phạm Minh Tuấn",
              "Vật Lý": "Thầy Trần Văn Đức", "Hóa Học": "Cô Đỗ Lan Anh", "Tin Học": "Thầy Phạm Minh Tuấn"}
    db.execute("DELETE FROM schedules")
    for wd in range(6):
        for p in range(1, 6):
            sj = subj_cycle[(wd * 5 + p) % len(subj_cycle)]
            st, et = PERIODS_DEFAULT[p - 1][2], PERIODS_DEFAULT[p - 1][3]
            for cl, room in [("12A1", "A201"), ("12A2", "A202"), ("12A3", "A203")]:
                db.execute("INSERT INTO schedules(weekday,period,subject,teacher,room,class_name,start_time,end_time) VALUES(?,?,?,?,?,?,?,?)",
                           (wd, p, sj, gv_map.get(sj, "GVCN"), room, cl, st, et))
    # Điểm danh 30 ngày (T2-T7, tiết 1-3)
    codes = [f"HS{i:03d}" for i in range(1, 31)]
    cl_of = {c: ("12A1" if int(c[2:]) <= 10 else ("12A2" if int(c[2:]) <= 20 else "12A3")) for c in codes}
    subj_of = {1: "Toán", 2: "Ngữ Văn", 3: "Tiếng Anh"}
    for back in range(30):
        d = (date.today() - timedelta(days=back)).isoformat()
        if date.fromisoformat(d).weekday() == 6:
            continue
        for p in (1, 2, 3):
            st = PERIODS_DEFAULT[p - 1][2]
            for code in codes:
                r = random.random()
                hh, mm = int(st[:2]), int(st[3:])
                if r < 0.85:
                    status, tm = "Có mặt", f"{hh:02d}:{mm + random.randint(0, 4):02d}"
                elif r < 0.92:
                    status, tm = "Đi trễ", f"{hh:02d}:{mm + random.randint(6, 14):02d}"
                elif r < 0.96:
                    status, tm = "Có phép", ""
                else:
                    continue
                db.execute("INSERT OR IGNORE INTO attendance(date,period,subject,student_code,class_name,time,status,method) VALUES(?,?,?,?,?,?,?,?)",
                           (d, p, subj_of[p], code, cl_of[code], tm, status, "demo"))
    # Thông báo demo
    db.execute("DELETE FROM notifications")
    for t, b, tp in [("Nguyễn Văn An vừa điểm danh", "HS001 • 12A1 • Tiết 1 lúc 07:02", "success"),
                     ("12A3 có 5 học sinh vắng", "Tiết 1 ngày hôm nay", "danger"),
                     ("Có 3 học sinh đi trễ tiết 1", "Vượt ngưỡng 07:05", "warning")]:
        db.execute("INSERT INTO notifications(title,body,type,created_at) VALUES(?,?,?,?)", (t, b, tp, now))
    db.commit()
