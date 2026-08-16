"""

Centralized configuration for the Flask application.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-finance-insights-secret-key-2026')
    DATABASE = os.path.join(BASE_DIR, 'finance.db')
    EXPORT_FOLDER = os.path.join(BASE_DIR, 'exports')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    DEBUG = True

    # Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # Currency
    CURRENCY_SYMBOL = '₹'
    CURRENCY_CODE = 'INR'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
