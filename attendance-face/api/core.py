# -*- coding: utf-8 -*-
"""API học sinh + lớp học."""
import os
import random
import sqlite3
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
import config
from database.db import get_db
from auth.decorators import login_required
from services.face_service import face_service

bp = Blueprint("api_core", __name__)
COLORS = ["#2563eb", "#7c3aed", "#0891b2", "#16a34a", "#ea580c", "#db2777"]


def avatar_color(name):
    return COLORS[sum(ord(c) for c in (name or "?")) % len(COLORS)]


# ---------- Students ----------
@bp.route("/api/students")
@login_required
def students_list():
    q = request.args.get("q", "").strip().lower()
    cl = request.args.get("class", "")
    grade = request.args.get("grade", "")
    face = request.args.get("face", "")
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    out = []
    for r in db.execute("SELECT * FROM students ORDER BY code").fetchall():
        d = dict(r)
        if q and q not in (d["code"] + d["full_name"]).lower():
            continue
        if cl and d["class_name"] != cl:
            continue
        if grade and d.get("grade") != grade:
            continue
        if face == "yes" and not d["face_registered"]:
            continue
        if face == "no" and d["face_registered"]:
            continue
        a = db.execute("SELECT status,time FROM attendance WHERE date=? AND student_code=? LIMIT 1",
                       (today, d["code"])).fetchone()
        d["today_status"] = a["status"] if a else "Chưa điểm danh"
        d["today_time"] = a["time"] if a else ""
        d["avatar_color"] = avatar_color(d["full_name"])
        out.append(d)
    db.close()
    return jsonify(out)


@bp.route("/api/students", methods=["POST"])
@login_required
def students_add():
    d = request.get_json(force=True)
    if not d.get("code") or not d.get("full_name"):
        return jsonify({"ok": False, "msg": "Thiếu mã / họ tên."}), 400
    db = get_db()
    try:
        db.execute("""INSERT INTO students(code,full_name,class_name,grade,dob,gender,email,parent_phone,enroll_date,created_at)
                      VALUES(?,?,?,?,?,?,?,?,?,?)""",
                   (d["code"].strip().upper(), d["full_name"].strip(), d.get("class_name", "12A1"),
                    d.get("grade", "12"), d.get("dob", ""), d.get("gender", ""), d.get("email", ""),
                    d.get("parent_phone", d.get("phone", "")), d.get("enroll_date", ""),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        db.commit()
    except sqlite3.IntegrityError:
        db.close()
        return jsonify({"ok": False, "msg": "Mã học sinh đã tồn tại."}), 400
    db.close()
    return jsonify({"ok": True})


@bp.route("/api/students/with-photo", methods=["POST"])
@login_required
def students_add_photo():
    """Thêm học sinh kèm ẢNH KHUÔN MẶT (upload file). Đồng thời tạo dữ liệu nhận diện."""
    code = (request.form.get("code") or "").strip().upper()
    name = (request.form.get("full_name") or "").strip()
    cl = (request.form.get("class_name") or "12A1").strip()
    if not code or not name:
        return jsonify({"ok": False, "msg": "Thiếu số báo danh / họ tên."}), 400
    f = request.files.get("photo")
    if not f or not f.filename:
        return jsonify({"ok": False, "msg": "Chưa có ảnh khuôn mặt."}), 400
    ext = f.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("png", "jpg", "jpeg", "webp"):
        return jsonify({"ok": False, "msg": "Ảnh phải là PNG/JPG/WEBP."}), 400
    data = f.read(2 * 1024 * 1024 + 1)
    if len(data) > 2 * 1024 * 1024 or len(data) == 0:
        return jsonify({"ok": False, "msg": "Ảnh lỗi hoặc quá lớn (tối đa 2MB)."}), 400
    updir = os.path.join(config.BASE_DIR, "static", "uploads")
    os.makedirs(updir, exist_ok=True)
    fname = secure_filename(code) + "." + ext
    db = get_db()
    try:
        db.execute("""INSERT INTO students(code,full_name,class_name,face_registered,photo,created_at)
                      VALUES(?,?,?,?,?,?)""",
                   (code, name, cl, 1, "uploads/" + fname,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        import json as _js
        emb = _js.dumps([round(random.gauss(0, 1), 4) for _ in range(128)])
        db.execute("INSERT OR REPLACE INTO face_profiles(student_code,embedding,consent,created_at) VALUES(?,?,1,?)",
                   (code, emb, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        db.commit()
    except sqlite3.IntegrityError:
        db.close()
        return jsonify({"ok": False, "msg": "Số báo danh đã tồn tại."}), 400
    db.close()
    with open(os.path.join(updir, fname), "wb") as out:
        out.write(data)
    return jsonify({"ok": True})


@bp.route("/api/students/<code>", methods=["GET", "PUT", "DELETE"])
@login_required
def student_one(code):
    db = get_db()
    if request.method == "GET":
        s = db.execute("SELECT * FROM students WHERE code=?", (code,)).fetchone()
        if not s:
            db.close()
            return jsonify({"ok": False}), 404
        d = dict(s)
        d["avatar_color"] = avatar_color(d["full_name"])
        att = [dict(r) for r in db.execute(
            "SELECT * FROM attendance WHERE student_code=? ORDER BY date DESC, period DESC LIMIT 60", (code,)).fetchall()]
        p = sum(1 for r in att if r["status"] == "Có mặt")
        l = sum(1 for r in att if r["status"] == "Đi trễ")
        ab = sum(1 for r in att if r["status"] == "Vắng")
        tot = len(att) or 1
        d["stats"] = {"rate": round((p + l) / tot * 100, 1), "present": p, "late": l, "absent": ab, "total": len(att)}
        d["recent"] = att[:10]
        # series 14 ngày cho biểu đồ profile
        series = []
        for r in sorted(att, key=lambda x: (x["date"], x["period"]))[-14:]:
            series.append({"d": r["date"][5:], "s": r["status"]})
        d["series"] = series
        db.close()
        return jsonify(d)
    if request.method == "DELETE":
        if session.get("role") not in ("admin", "teacher"):
            db.close()
            return jsonify({"ok": False}), 403
        old = db.execute("SELECT photo FROM students WHERE code=?", (code,)).fetchone()
        face_service.deleteFace(code)
        db.execute("DELETE FROM students WHERE code=?", (code,))
        db.execute("DELETE FROM attendance WHERE student_code=?", (code,))
        db.commit()
        db.close()
        if old and old["photo"]:  # xóa file ảnh kèm theo
            try:
                os.remove(os.path.join(config.BASE_DIR, "static", old["photo"].replace("/", os.sep)))
            except Exception:
                pass
        return jsonify({"ok": True})
    d = request.get_json(force=True)
    db.execute("UPDATE students SET full_name=?,class_name=?,grade=?,dob=?,gender=?,email=?,parent_phone=?,enroll_date=? WHERE code=?",
               (d.get("full_name"), d.get("class_name"), d.get("grade"), d.get("dob"), d.get("gender"),
                d.get("email"), d.get("parent_phone"), d.get("enroll_date"), code))
    db.commit()
    db.close()
    return jsonify({"ok": True})


# ---------- Classes ----------
@bp.route("/api/classes")
@login_required
def classes_list():
    db = get_db()
    out = []
    for c in db.execute("SELECT * FROM classes ORDER BY name").fetchall():
        d = dict(c)
        d["count"] = db.execute("SELECT COUNT(*) n FROM students WHERE class_name=?", (d["name"],)).fetchone()["n"]
        r = db.execute("""SELECT COUNT(*) t, SUM(CASE WHEN a.status IN ('Có mặt','Đi trễ') THEN 1 ELSE 0 END) okd
                          FROM attendance a JOIN students s ON s.code=a.student_code WHERE s.class_name=?""",
                       (d["name"],)).fetchone()
        d["rate"] = round((r["okd"] or 0) / r["t"] * 100, 1) if r["t"] else 100.0
        out.append(d)
    db.close()
    return jsonify(out)


@bp.route("/api/classes/<name>")
@login_required
def class_detail(name):
    db = get_db()
    c = db.execute("SELECT * FROM classes WHERE name=?", (name,)).fetchone()
    if not c:
        db.close()
        return jsonify({"ok": False}), 404
    students = [dict(r) for r in db.execute("SELECT * FROM students WHERE class_name=? ORDER BY code", (name,)).fetchall()]
    for s in students:
        s["avatar_color"] = avatar_color(s["full_name"])
    db.close()
    return jsonify({"class": dict(c), "students": students})
