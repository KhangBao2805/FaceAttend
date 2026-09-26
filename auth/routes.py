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


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@bp.route("/api/forgot", methods=["POST"])
def forgot():
    # Mock: ghi nhận yêu cầu, bản thật gửi email reset token
    return jsonify({"ok": True, "msg": "Đã gửi link đặt lại mật khẩu (demo)."})
