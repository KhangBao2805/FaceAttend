# -*- coding: utf-8 -*-
"""Tính toán KPI dashboard + analytics."""
from datetime import date, timedelta
from database.db import get_db


def _counts(db, day):
    rows = db.execute("SELECT status FROM attendance WHERE date=?", (day,)).fetchall()
    c = {"present": 0, "late": 0, "leave": 0, "checked": len(rows)}
    for r in rows:
        if r["status"] == "Có mặt":
            c["present"] += 1
        elif r["status"] == "Đi trễ":
            c["late"] += 1
        elif r["status"] == "Có phép":
            c["leave"] += 1
    return c


def kpi(day):
    db = get_db()
    total = db.execute("SELECT COUNT(*) c FROM students").fetchone()["c"]
    t = _counts(db, day)
    y = _counts(db, (date.fromisoformat(day) - timedelta(days=1)).isoformat())
    db.close()
    absent = max(total - t["checked"], 0)
    rate = round(t["checked"] / total * 100, 1) if total else 0

    def delta(cur, prev):
        if not prev:
            return (100.0 if cur else 0.0, cur >= prev)
        return (round((cur - prev) / prev * 100, 1), cur >= prev)
    d_present = delta(t["present"], y["present"])
    return {"total": total, "present": t["present"], "late": t["late"],
            "absent": absent, "leave": t["leave"], "checked": t["checked"],
            "rate": rate, "delta_present": d_present[0], "up": d_present[1]}


def overview(day, days=7):
    db = get_db()
    out = []
    for i in range(days - 1, -1, -1):
        dd = (date.fromisoformat(day) - timedelta(days=i)).isoformat()
        r = db.execute("""SELECT
            SUM(CASE WHEN status='Có mặt' THEN 1 ELSE 0 END) p,
            SUM(CASE WHEN status='Đi trễ' THEN 1 ELSE 0 END) l,
            COUNT(*) c FROM attendance WHERE date=?""", (dd,)).fetchone()
        total = db.execute("SELECT COUNT(*) c FROM students").fetchone()["c"]
        out.append({"date": dd[5:], "present": r["p"] or 0, "late": r["l"] or 0,
                    "absent": max(total - (r["c"] or 0), 0)})
    db.close()
    return out


def by_class(day=None):
    db = get_db()
    q = """SELECT s.class_name lop, COUNT(*) tong,
           SUM(CASE WHEN a.status='Có mặt' THEN 1 ELSE 0 END) comat,
           SUM(CASE WHEN a.status='Đi trễ' THEN 1 ELSE 0 END) ditre
           FROM attendance a JOIN students s ON s.code=a.student_code"""
    args = []
    if day:
        q += " WHERE a.date=?"
        args.append(day)
    q += " GROUP BY s.class_name ORDER BY lop"
    rows = [dict(r) for r in db.execute(q, args).fetchall()]
    db.close()
    return rows
