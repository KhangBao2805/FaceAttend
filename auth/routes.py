# -*- coding: utf-8 -*-
"""Auth: login / logout (remember-me + forgot mock)."""
from datetime import timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash
from database.db import get_db

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    err = None
    if request.method == "POST":
        un = request.form.get("username", "").strip()
        pw = request.form.get("password", "")
        remember = request.form.get("remember") == "on"
        db = get_db()
        u = db.execute("SELECT * FROM users WHERE username=? OR email=?", (un, un)).fetchone()
        db.close()
        if u and check_password_hash(u["password_hash"], pw):
            session["uid"], session["role"] = u["id"], u["role"]
            session["name"], session["username"] = u["full_name"], u["username"]
            session.permanent = remember
            return redirect(url_for("pages.dashboard"))
        err = "Sai tài khoản hoặc mật khẩu."
    return render_template("pages/login.html", err=err)


@bp.route("/setup", methods=["GET", "POST"])
def setup():
    """Tạo Admin đầu tiên (chỉ khi chưa có tài khoản nào). Dùng cho hosting mới."""
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    db = get_db()
    n = db.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
    if n > 0:
        db.close()
        return "Đã có tài khoản. Trang setup đã khóa.", 403
    err = None
    if request.method == "POST":
        un = request.form.get("username", "").strip()
        pw = request.form.get("password", "")
        fn = request.form.get("full_name", "").strip() or un
        if not un or not pw:
            err = "Nhập đủ tên đăng nhập và mật khẩu."
        else:
            db.execute("INSERT INTO users(username,password_hash,role,full_name,created_at) VALUES(?,?,?,?,?)",
                       (un, generate_password_hash(pw), "admin", fn,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            db.commit()
            db.close()
            return redirect(url_for("auth.login"))
    db.close()
    return render_template("pages/setup.html", err=err)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@bp.route("/api/forgot", methods=["POST"])
def forgot():
    # Mock: ghi nhận yêu cầu, bản thật gửi email reset token
    return jsonify({"ok": True, "msg": "Đã gửi link đặt lại mật khẩu (demo)."})
