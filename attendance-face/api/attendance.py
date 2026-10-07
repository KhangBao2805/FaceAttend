# -*- coding: utf-8 -*-
"""API điểm danh + khuôn mặt + thời khóa biểu."""
import csv
import io
import random
from datetime import date, datetime
from flask import Blueprint, request, jsonify, session, Response
from database.db import get_db
from auth.decorators import login_required, admin_required
from services.face_service import face_service
from services import attendance_service

bp = Blueprint("api_att", __name__)


# ---------- Face ----------
@bp.route("/api/face/register", methods=["POST"])
@login_required
def face_register():
    d = request.get_json(force=True)
    return jsonify(face_service.registerFace(d.get("student_code"), d.get("embedding"), d.get("consent", False)))


@bp.route("/api/face/recognize", methods=["POST"])
@login_required
def face_recognize():
    d = request.get_json(force=True)
    return jsonify(face_service.recognizeFace(d.get("embedding")))


@bp.route("/api/face/verify", methods=["POST"])
@login_required
def face_verify():
    d = request.get_json(force=True)
    return jsonify(face_service.verifyFace(d.get("student_code"), d.get("embedding")))


@bp.route("/api/face/recognize_mock", methods=["POST"])
def face_mock():
    """Giả lập camera cho máy quét CÔNG CỘNG — không cần đăng nhập."""
    d = request.get_json(force=True) or {}
    day = d.get("date") or date.today().isoformat()
    p = int(d.get("period") or 1)
    db = get_db()
    done = {r["student_code"] for r in
            db.execute("SELECT student_code FROM attendance WHERE date=? AND period=?", (day, p)).fetchall()}
    cands = [dict(r) for r in db.execute("SELECT * FROM students WHERE face_registered=1 ORDER BY code").fetchall()
             if r["code"] not in done]
    db.close()
    if not cands:
        return jsonify({"ok": False, "msg": "Tất cả học sinh đã điểm danh xong tiết này."})
    s = random.choice(cands)
    return jsonify({"ok": True, "student_code": s["code"], "full_name": s["full_name"],
                    "class_name": s["class_name"], "mode": "mock"})


@bp.route("/api/face/delete/<code>", methods=["POST"])
@login_required
def face_delete(code):
    return jsonify(face_service.deleteFace(code))


# ---------- Attendance ----------
@bp.route("/api/attendance/checkin", methods=["POST"])
def checkin():
    """Ghi điểm danh từ máy quét công cộng — không cần đăng nhập."""
    d = request.get_json(force=True)
    res, status = attendance_service.checkin(
        d.get("student_code"), d.get("date") or date.today().isoformat(),
        int(d.get("period") or 1), d.get("subject", ""), d.get("method", "face"))
    return jsonify(res), status


@bp.route("/api/attendance/list")
@login_required
def att_list():
    f = request.args.get("from", request.args.get("date", ""))
    t = request.args.get("to", request.args.get("date", ""))
    cl = request.args.get("class", "")
    stt = request.args.get("status", "")
    subj = request.args.get("subject", "")
    q = request.args.get("q", "").lower()
    db = get_db()
    sql = """SELECT a.*, s.full_name FROM attendance a JOIN students s ON s.code=a.student_code WHERE 1=1"""
    args = []
    if f:
        sql += " AND a.date>=?"; args.append(f)
    if t:
        sql += " AND a.date<=?"; args.append(t)
    if cl:
        sql += " AND s.class_name=?"; args.append(cl)
    if stt:
        sql += " AND a.status=?"; args.append(stt)
    if subj:
        sql += " AND a.subject=?"; args.append(subj)
    sql += " ORDER BY a.date DESC, a.time DESC LIMIT 500"
    rows = [dict(r) for r in db.execute(sql, args).fetchall()]
    if q:
        rows = [r for r in rows if q in (r["student_code"] + r["full_name"]).lower()]
    if session.get("role") == "student":
        u = db.execute("SELECT linked_student_code FROM users WHERE id=?", (session["uid"],)).fetchone()
        mine = u["linked_student_code"] if u else ""
        rows = [r for r in rows if r["student_code"] == mine]
    db.close()
    return jsonify(rows)


@bp.route("/api/attendance/session")
def att_session():
    day = request.args.get("date", date.today().isoformat())
    p = int(request.args.get("period", 1))
    db = get_db()
    total = db.execute("SELECT COUNT(*) c FROM students").fetchone()["c"]
    rows = [dict(r) for r in db.execute(
        """SELECT a.*, s.full_name, s.class_name FROM attendance a
           JOIN students s ON s.code=a.student_code
           WHERE a.date=? AND a.period=? ORDER BY a.time DESC""", (day, p)).fetchall()]
    db.close()
    return jsonify({"total": total, "checked": len(rows), "records": rows})


def _filtered_rows(args):
    with_date = att_list.__wrapped__ if hasattr(att_list, "__wrapped__") else None
    return None  # placeholder (export tự truy vấn lại)


@bp.route("/history/export")
@login_required
def export_csv():
    db = get_db()
    rows = [dict(r) for r in db.execute(
        """SELECT a.date,a.period,a.subject,a.student_code,s.full_name,s.class_name,a.time,a.status
           FROM attendance a JOIN students s ON s.code=a.student_code ORDER BY a.date DESC LIMIT 2000""").fetchall()]
    db.close()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Ngay", "Tiet", "Mon", "MaHS", "HoTen", "Lop", "Gio", "TrangThai"])
    for r in rows:
        w.writerow([r["date"], r["period"], r["subject"], r["student_code"],
                    r["full_name"], r["class_name"], r["time"], r["status"]])
    buf.seek(0)
    return Response("\ufeff" + buf.read(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=faceattend.csv"})


@bp.route("/history/export-xlsx")
@login_required
def export_xlsx():
    from openpyxl import Workbook
    db = get_db()
    rows = db.execute(
        """SELECT a.date,a.period,a.subject,a.student_code,s.full_name,s.class_name,a.time,a.status
           FROM attendance a JOIN students s ON s.code=a.student_code ORDER BY a.date DESC LIMIT 2000""").fetchall()
    db.close()
    wb = Workbook()
    ws = wb.active
    ws.title = "DiemDanh"
    ws.append(["Ngày", "Tiết", "Môn", "Mã HS", "Họ tên", "Lớp", "Giờ", "Trạng thái"])
    for r in rows:
        ws.append(list(r))
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return Response(buf.read(),
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment;filename=faceattend.xlsx"})


# ---------- Schedule / periods ----------
@bp.route("/api/kiosk/faces")
def kiosk_faces():
    """Danh sách khuôn mặt đã đăng ký cho máy quét công cộng (chạy nội bộ)."""
    db = get_db()
    rows = [dict(r) for r in db.execute(
        "SELECT code, full_name, class_name, photo FROM students WHERE face_registered=1 AND photo IS NOT NULL AND photo<>'' ORDER BY code").fetchall()]
    db.close()
    return jsonify(rows)


@bp.route("/api/schedule")
@login_required
def schedule_list():
    db = get_db()
    rows = [dict(r) for r in db.execute("SELECT * FROM schedules ORDER BY weekday, period").fetchall()]
    db.close()
    return jsonify(rows)


@bp.route("/api/schedule", methods=["POST"])
@login_required
@admin_required
def schedule_add():
    d = request.get_json(force=True)
    db = get_db()
    db.execute("INSERT INTO schedules(weekday,period,subject,teacher,room,class_name,start_time,end_time) VALUES(?,?,?,?,?,?,?,?)",
               (int(d["weekday"]), int(d["period"]), d["subject"], d.get("teacher", ""),
                d.get("room", ""), d.get("class_name", "12A1"),
                d.get("start_time", ""), d.get("end_time", "")))
    db.commit()
    db.close()
    return jsonify({"ok": True})


@bp.route("/api/schedule/<int:sid>", methods=["DELETE"])
@login_required
@admin_required
def schedule_del(sid):
    db = get_db()
    db.execute("DELETE FROM schedules WHERE id=?", (sid,))
    db.commit()
    db.close()
    return jsonify({"ok": True})


@bp.route("/api/periods", methods=["POST"])
@login_required
@admin_required
def periods_save():
    for item in request.get_json(force=True):
        db = get_db()
        db.execute("UPDATE periods SET start_time=?,end_time=?,session=? WHERE period=?",
                   (item["start_time"], item["end_time"], item.get("session", ""), int(item["period"])))
        db.commit()
        db.close()
    return jsonify({"ok": True})
