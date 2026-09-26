# -*- coding: utf-8 -*-
"""Lớp kết nối DB dùng chung."""
import os
import sqlite3
import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_db():
    c = sqlite3.connect(config.DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_schema():
    schema = os.path.join(BASE_DIR, "database", "schema.sql")
    db = get_db()
    with open(schema, encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()
    db.close()
