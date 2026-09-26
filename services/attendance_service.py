# -*- coding: utf-8 -*-
"""Nghiệp vụ điểm danh: chống trùng + tính trạng thái theo giờ tiết."""
from datetime import datetime, date
from database.db import get_db
import config


def status_for(start_time):
    now_t = datetime.now().strftime("%H:%M")
    try:
        diff = (datetime.strptime(now_t, "%H:%M") - datetime.strptime(start_time, "%H:%M")).total_seconds() / 60
    except Exception:
        return "Có mặt"
    return "Có mặt" if diff <= config.LATE_AFTER_MINUTES else "Đi trễ"


def checkin(student_code, day, period, subject, method="face"):
    db = get_db()
    st = db.execute("SELECT * FROM students WHERE code=?", (student_code,)).fetchone()
    if not st:
        db.close()
        return {"ok": False, "msg": "Không tìm thấy học sinh."}, 404
    dup = db.execute("SELECT * FROM attendance WHERE date=? AND period=? AND student_code=?",
                     (day, period, student_code)).fetchone()
    if dup:  # chống điểm danh trùng: không tạo bản ghi mới
        db.close()
        return {"ok": False, "msg": "Đã điểm danh",
                "detail": f"Bạn đã được điểm danh trong tiết này lúc {dup['time']}."}, 200
    prow = db.execute("SELECT * FROM periods WHERE period=?", (period,)).fetchone()
    status = status_for(prow["start_time"]) if (day == date.today().isoformat() and prow) else "Có mặt"
    now_t = datetime.now().strftime("%H:%M")
    db.execute("""INSERT INTO attendance(date,period,subject,student_code,class_name,time,status,method)
                  VALUES(?,?,?,?,?,?,?,?)""",
               (day, period, subject, student_code, st["class_name"], now_t, status, method))
    db.execute("INSERT INTO notifications(title,body,type,created_at) VALUES(?,?,?,?)",
               (f"{st['full_name']} vừa điểm danh",
                f"{student_code} • {st['class_name']} • Tiết {period} lúc {now_t}",
                "success", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    db.commit()
    db.close()
    return {"ok": True, "msg": "Đã điểm danh", "full_name": st["full_name"],
            "class_name": st["class_name"], "time": now_t, "status": status}, 200
