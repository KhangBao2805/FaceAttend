# -*- coding: utf-8 -*-
"""Page routes.
- / : trang quét điểm danh CÔNG CỘNG (không cần đăng nhập) — đặt máy quét ở cổng lớp.
- Còn lại: khu vực GIÁO VIÊN (cần đăng nhập role admin/teacher).
"""
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, session
from database.db import get_db
from auth.decorators import teacher_required

bp = Blueprint("pages", __name__)


def ctx(active):
    return {"user": {"name": session.get("name"), "role": session.get("role"),
                     "username": session.get("username")},
            "today": date.today().isoformat(), "active": active,
            "school_name": "Trường THPT Nguyễn Du - Ninh Sơn"}


@bp.route("/")
def kiosk():
    """Trang quét công cộng cho học sinh — không login."""
    db = get_db()
    periods = [dict(r) for r in db.execute("SELECT * FROM periods ORDER BY period").fetchall()]
    classes = [r["name"] for r in db.execute("SELECT name FROM classes ORDER BY name").fetchall()]
    db.close()
    return render_template("pages/kiosk.html", today=date.today().isoformat(),
                           periods=periods, classes=classes,
                           school_name="Trường THPT Nguyễn Du - Ninh Sơn")


@bp.route("/dashboard")
@teacher_required
def dashboard():
    return render_template("pages/dashboard.html", **ctx("dashboard"))


@bp.route("/them-hoc-sinh")
@teacher_required
def add_student():
    db = get_db()
    classes = [r["name"] for r in db.execute("SELECT name FROM classes ORDER BY name").fetchall()]
    db.close()
    return render_template("pages/add_student.html", **ctx("add_student"), classes=classes or ["12A1"])


@bp.route("/thoi-khoa-bieu")
@teacher_required
def schedule():
    return render_template("pages/schedule.html", **ctx("schedule"))


@bp.route("/lich-su")
@teacher_required
def history():
    return render_template("pages/history.html", **ctx("history"))


@bp.route("/thong-ke")
@teacher_required
def statistics():
    return render_template("pages/statistics.html", **ctx("stats"))


@bp.route("/tai-khoan")
@teacher_required
def accounts():
    if session.get("role") != "admin":
        return "Cần quyền Admin.", 403
    return render_template("pages/accounts.html", **ctx("accounts"))


@bp.route("/cai-dat")
@teacher_required
def settings():
    if session.get("role") != "admin":
        return "Cần quyền Admin.", 403
    db = get_db()
    periods = [dict(r) for r in db.execute("SELECT * FROM periods ORDER BY period").fetchall()]
    db.close()
    return render_template("pages/settings.html", **ctx("settings"), periods=periods)
