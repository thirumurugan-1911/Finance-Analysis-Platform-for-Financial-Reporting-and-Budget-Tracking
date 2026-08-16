"""

A comprehensive personal finance management web application built with Flask.

Combines ALL features from Milestones 1-4:
  M1: Core Finance (Auth, Expenses, Budget, Dashboard, AI Analysis)
  M2: Investments & Goals (Portfolio, Asset Allocation, Goal Planning, Analytics)
  M3: Intelligence (Spending Analysis, Budget Recs, Health Score, Alerts, AI Insights)
  M4: Reporting (Reports, PDF/Excel Export, Dashboard Optimization, JARVIS AI Assistant)

Usage:
  1. python init_db.py      (initialize database with sample data)
  2. python app.py          (start the server)
  3. Open http://localhost:5000
  4. Login: demo@smartfinance.com / demo123
"""
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import config
from utils.db import init_app as init_db_app, query_db, execute_db
from utils.helpers import login_required, get_current_month, get_current_year, calculate_percentage

# Import all blueprints
from modules.auth import bp as auth_bp
from modules.expenses import bp as expenses_bp
from modules.budget import bp as budget_bp
from modules.investments import bp as investments_bp
from modules.goals import bp as goals_bp
from modules.dashboard import bp as dashboard_bp
from modules.intelligence import bp as intelligence_bp
from modules.notifications import bp as notifications_bp
from modules.reports import bp as reports_bp
from modules.export import bp as export_bp
from modules.jarvis import bp as jarvis_bp


def create_app(config_name='default'):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure export directory exists
    os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)

    # Register database
    init_db_app(app)

    # Auto-initialize database on first run
    with app.app_context():
        from utils.db import get_db
        try:
            db = get_db()
            db.execute("SELECT 1 FROM users LIMIT 1")
            db.close()
        except Exception:
            # Database not initialized - run init
            db.close() if 'db' in locals() else None
            from init_db import create_tables, seed_sample_data
            create_tables()
            seed_sample_data()

    # Register all blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(investments_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(intelligence_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(jarvis_bp)

    # Template context processor - inject common data
    @app.context_processor
    def inject_globals():
        notifications_count = 0
        if 'user_id' in session:
            try:
                row = query_db(
                    "SELECT COUNT(*) as cnt FROM notifications WHERE user_id=? AND status='Active'",
                    (session['user_id'],), one=True
                )
                notifications_count = row['cnt'] if row else 0
            except Exception:
                notifications_count = 0
        return dict(
            app_name='Smart Finance Insights',
            current_year=get_current_year(),
            notifications_count=notifications_count,
            calculate_percentage=calculate_percentage,
            current_month=get_current_month(),
            min=min,
            max=max,
            abs=abs,
            round=round
        )

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error_code=404,
                               error_message='Page Not Found'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('error.html', error_code=500,
                               error_message='Internal Server Error'), 500

    return app


app = create_app('default')


if __name__ == '__main__':
    print("=" * 60)
    print("  Smart Finance Insights - Starting Server...")
    print("=" * 60)
    print("  Login: demo@smartfinance.com / demo123")
    print("  URL:   http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
