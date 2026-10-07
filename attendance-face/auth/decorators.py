# -*- coding: utf-8 -*-
"""Decorator phân quyền dùng chung."""
from functools import wraps
from flask import session, redirect, url_for, jsonify


def login_required(fn):
    @wraps(fn)
    def wrap(*a, **kw):
        if "uid" not in session:
            if "/api/" in (fn.__module__ or "") or str(fn).find("api") >= 0:
                return jsonify({"ok": False, "msg": "Chưa đăng nhập."}), 401
            return redirect(url_for("auth.login"))
        return fn(*a, **kw)
    return wrap


def admin_required(fn):
    @wraps(fn)
    def wrap(*a, **kw):
        if session.get("role") != "admin":
            return jsonify({"ok": False, "msg": "Cần quyền Admin."}), 403
        return fn(*a, **kw)
    return wrap


def teacher_required(fn):
    """Khu vực giáo viên: chỉ Admin hoặc Giáo viên. Chưa login -> về trang login."""
    @wraps(fn)
    def wrap(*a, **kw):
        if "uid" not in session:
            return redirect(url_for("auth.login"))
        if session.get("role") not in ("admin", "teacher"):
            return redirect(url_for("auth.login"))
        return fn(*a, **kw)
    return wrap
