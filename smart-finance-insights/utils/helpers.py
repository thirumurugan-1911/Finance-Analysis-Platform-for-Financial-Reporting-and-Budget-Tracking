"""
Smart Finance Insights - Helper Utilities
Currency formatting, password hashing, decorators, and common helpers.
"""
import hashlib
import os
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, flash, current_app


# ---------- Currency / Number Formatting ----------
def format_currency(amount):
    """Format a number as Indian Rupee currency."""
    try:
        amt = float(amount or 0)
    except (TypeError, ValueError):
        amt = 0.0
    symbol = current_app.config.get('CURRENCY_SYMBOL', '₹') if current_app else '₹'
    # Indian number formatting (lakhs/crores)
    if amt == 0:
        return f"{symbol}0"
    neg = amt < 0
    amt = abs(amt)
    whole = int(amt)
    decimal = round((amt - whole) * 100)
    s = str(whole)
    if len(s) > 3:
        last3 = s[-3:]
        rest = s[:-3]
        # Group rest in pairs from right (Indian style)
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        formatted = ','.join(groups) + ',' + last3
    else:
        formatted = s
    if decimal > 0:
        formatted += f".{decimal:02d}"
    return f"{'-' if neg else ''}{symbol}{formatted}"


def format_number(amount):
    """Format number with thousand separators."""
    try:
        amt = float(amount or 0)
    except (TypeError, ValueError):
        amt = 0.0
    return f"{amt:,.2f}"


def format_percentage(value, decimals=1):
    """Format a value as percentage."""
    try:
        v = float(value or 0)
    except (TypeError, ValueError):
        v = 0.0
    return f"{v:.{decimals}f}%"


def calculate_percentage(part, total):
    """Calculate percentage safely."""
    try:
        total = float(total or 0)
        part = float(part or 0)
        if total == 0:
            return 0.0
        return round((part / total) * 100, 2)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0


# ---------- Date Helpers ----------
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']


def get_month_name(month_num):
    """Get month name from number (1-12)."""
    try:
        idx = int(month_num) - 1
        if 0 <= idx < 12:
            return MONTHS[idx]
    except (TypeError, ValueError):
        pass
    return ''


def get_current_month():
    """Return current month as number (1-12)."""
    return datetime.now().month


def get_current_year():
    """Return current year."""
    return datetime.now().year


def get_current_date():
    """Return current date as YYYY-MM-DD string."""
    return datetime.now().strftime('%Y-%m-%d')


# ---------- Security ----------
def hash_password(password):
    """Hash a password using SHA-256 with salt (simple, no external deps)."""
    salt = 'smart_finance_salt_2026'
    return hashlib.sha256((password + salt).encode()).hexdigest()


def verify_password(password, hashed):
    """Verify a password against its hash."""
    return hash_password(password) == hashed


# ---------- Auth Decorator ----------
def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_user_id():
    """Get current logged-in user's ID."""
    return session.get('user_id')


# ---------- Safe Conversions ----------
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
