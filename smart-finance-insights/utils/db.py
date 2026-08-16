"""
Smart Finance Insights - Database Helper
Provides centralized database connection and query helpers using SQLite.
"""
import sqlite3
from functools import wraps
from flask import g, current_app


def get_db():
    """Get a database connection for the current request context."""
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """Execute a SELECT query and return results."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def execute_db(query, args=()):
    """Execute an INSERT/UPDATE/DELETE query and commit."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id


def init_app(app):
    """Register database teardown with the Flask app."""
    app.teardown_appcontext(close_db)
