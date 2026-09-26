# -*- coding: utf-8 -*-
"""API dashboard / thống kê / thông báo / tài khoản."""
from datetime import date
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash
from database.db import get_db
from auth.decorators import login_required, admin_required
from services import stats_service
import sqlite3

bp = Blueprint("api_misc", __name__)


@bp.route("/api/dashboard")
@login_required
def dashboard():
    day = request.args.get("date", date.today().isoformat())
    days = int(request.args.get("days", 7))
    k = stats_service.kpi(day)
    chart = stats_service.overview(day, days)
    byc = stats_service.by_class(day)
    db = get_db()
    recent = [dict(r) for r in db.execute(
        """SELECT a.*, s.full_name, s.class_name FROM attendance a
           JOIN students s ON s.code=a.student_code
           WHERE a.date=? ORDER BY a.time DESC LIMIT 8""", (day,)).fetchall()]
    db.close()
    return jsonify({**k, "chart": chart, "by_class": byc, "recent": recent})


@bp.route("/api/statistics")
@login_required
def statistics():
    day = request.args.get("date", date.today().isoformat())
    days = int(request.args.get("days", 30))
    db = get_db()
    rows = db.execute("SELECT status FROM attendance").fetchall()
    total = len(rows) or 1
    pct = lambda s: round(sum(1 for r in rows if r["status"] == s) / total * 100, 1)
    # top đi trễ
    top = [dict(r) for r in db.execute(
        """SELECT s.code, s.full_name, s.class_name, COUNT(*) n FROM attendance a
           JOIN students s ON s.code=a.student_code WHERE a.status='Đi trễ'
           GROUP BY s.code ORDER BY n DESC LIMIT 8""").fetchall()]
    db.close()
    return jsonify({"ti_le_di_hoc": pct("Có mặt"), "ti_le_di_tre": pct("Đi trễ"),
                    "ti_le_co_phep": pct("Có phép"), "tong_luot": len(rows),
                    "theo_lop": stats_service.by_class(),
                    "overview": stats_service.overview(day, min(days, 30)),
                    "top_late": top})


@bp.route("/api/notifications")
@login_required
def notif_list():
    db = get_db()
    rows = [dict(r) for r in db.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 20").fetchall()]
    unread = sum(1 for r in rows if not r["is_read"])
    db.close()
    return jsonify({"items": rows, "unread": unread})


@bp.route("/api/notifications/read", methods=["POST"])
@login_required
def notif_read():
    db = get_db()
    nid = (request.get_json(force=True) or {}).get("id")
    if nid:
        db.execute("UPDATE notifications SET is_read=1 WHERE id=?", (nid,))
    else:
        db.execute("UPDATE notifications SET is_read=1")
    db.commit()
    db.close()
    return jsonify({"ok": True})


@bp.route("/api/users")
@login_required
@admin_required
def users_list():
    db = get_db()
    rows = [dict(r) for r in db.execute(
        "SELECT id,username,email,role,full_name,linked_student_code,created_at FROM users").fetchall()]
    db.close()
    return jsonify(rows)


@bp.route("/api/users", methods=["POST"])
@login_required
@admin_required
def users_add():
    d = request.get_json(force=True)
    db = get_db()
    try:
        from datetime import datetime
        db.execute("INSERT INTO users(username,email,password_hash,role,full_name,linked_student_code,created_at) VALUES(?,?,?,?,?,?,?)",
                   (d["username"], d.get("email", ""), generate_password_hash(d["password"]),
                    d.get("role", "teacher"), d.get("full_name", ""),
                    d.get("linked_student_code") or None,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        db.commit()
    except sqlite3.IntegrityError:
        db.close()
        return jsonify({"ok": False, "msg": "Tên đăng nhập đã tồn tại."}), 400
    db.close()
    return jsonify({"ok": True})
