"""
JARVIS - AI Financial Assistant Module
Milestone 4 - Final Deliverable
Interactive chatbot that answers finance queries, provides insights,
retrieves expense summaries, budget recommendations, investment analysis,
and goal tracking through natural language.
"""
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from utils.db import query_db, execute_db
from utils.helpers import (login_required, get_current_month, get_current_year,
                           get_month_name, calculate_percentage, format_currency)
from modules.analysis import get_spending_analysis, get_budget_recommendations
from modules.insights import get_ai_insights
from modules.health_score import get_health_score

bp = Blueprint('jarvis', __name__, url_prefix='')


def _get_financial_summary(user_id):
    """Get a quick financial summary for JARVIS responses."""
    month = get_current_month()
    year = get_current_year()
    month_str = f"{year}-{month:02d}"

    income_row = query_db(
        "SELECT COALESCE(SUM(amount),0) as total FROM income WHERE user_id=? AND strftime('%Y-%m', date)=?",
        (user_id, month_str), one=True
    )
    expense_row = query_db(
        "SELECT COALESCE(SUM(amount),0) as total FROM expenses WHERE user_id=? AND strftime('%Y-%m', date)=?",
        (user_id, month_str), one=True
    )
    inv_row = query_db(
        "SELECT COALESCE(SUM(invested_amount),0) as invested, COALESCE(SUM(current_value),0) as current FROM investments WHERE user_id=?",
        (user_id,), one=True
    )
    goals = query_db("SELECT COUNT(*) as cnt FROM goals WHERE user_id=?", (user_id,), one=True)

    return {
        'income': income_row['total'] if income_row else 0,
        'expense': expense_row['total'] if expense_row else 0,
        'savings': (income_row['total'] if income_row else 0) - (expense_row['total'] if expense_row else 0),
        'invested': inv_row['invested'] if inv_row else 0,
        'current_value': inv_row['current'] if inv_row else 0,
        'goals_count': goals['cnt'] if goals else 0,
        'month_name': get_month_name(month),
        'year': year
    }


def _process_query(user_id, message):
    """Process user's natural language query and generate JARVIS response."""
    msg = message.lower().strip()
    summary = _get_financial_summary(user_id)

    # --- Greetings ---
    if any(g in msg for g in ['hello', 'hi', 'hey', 'greetings', 'jarvis']):
        return (f"Hello! I'm JARVIS, your AI Financial Assistant. \U0001F916\n\n"
                f"Here's your quick summary for {summary['month_name']} {summary['year']}:\n"
                f"• Income: {format_currency(summary['income'])}\n"
                f"• Expenses: {format_currency(summary['expense'])}\n"
                f"• Savings: {format_currency(summary['savings'])}\n"
                f"• Investments: {format_currency(summary['current_value'])}\n\n"
                f"How can I help you today? You can ask about expenses, budget, investments, goals, or financial advice.")

    # --- Expense queries ---
    if any(w in msg for w in ['expense', 'spend', 'spent', 'expenditure']):
        if any(w in msg for w in ['category', 'categories', 'breakdown']):
            analysis = get_spending_analysis(user_id)
            lines = [f"\U0001F4CA Spending Breakdown for {analysis['month_name']} {analysis['year']}:\n"]
            for c in analysis['categories'][:6]:
                lines.append(f"• {c['category']}: {format_currency(c['amount'])} ({c['percentage']:.1f}%)")
            lines.append(f"\nTotal Expenses: {format_currency(analysis['total_expense'])}")
            lines.append(f"Average Daily: {format_currency(analysis['avg_daily'])}")
            if analysis['high_spending']:
                lines.append(f"\n⚠️ High spending categories: {', '.join(c['category'] for c in analysis['high_spending'])}")
            return '\n'.join(lines)

        if any(w in msg for w in ['total', 'how much', 'sum']):
            return (f"\U0001F4B8 Your total expenses for {summary['month_name']} {summary['year']} "
                    f"are {format_currency(summary['expense'])}.\n"
                    f"Compared to income of {format_currency(summary['income'])}, "
                    f"your expense ratio is {calculate_percentage(summary['expense'], summary['income']):.1f}%.")

        analysis = get_spending_analysis(user_id)
        lines = [f"\U0001F4CA Expense Summary for {analysis['month_name']} {analysis['year']}:\n"]
        lines.append(f"Total Expenses: {format_currency(analysis['total_expense'])}")
        lines.append(f"Number of Transactions: {analysis['transaction_count']}")
        lines.append(f"Average Daily Spending: {format_currency(analysis['avg_daily'])}\n")
        lines.append("Top Spending Categories:")
        for c in analysis['categories'][:3]:
            lines.append(f"  • {c['category']}: {format_currency(c['amount'])} ({c['percentage']:.1f}%)")
        return '\n'.join(lines)

    # --- Budget queries ---
    if any(w in msg for w in ['budget', 'limit', 'budget recommendation']):
        recs = get_budget_recommendations(user_id)
        lines = ["\U0001F4CB Budget Recommendations:\n"]
        high_recs = [r for r in recs['recommendations'] if r['priority'] == 'High']
        if high_recs:
            lines.append("⚠️ Urgent Actions:")
            for r in high_recs:
                lines.append(f"  • {r['message']}")
            lines.append("")
        other_recs = [r for r in recs['recommendations'] if r['priority'] != 'High']
        if other_recs:
            lines.append("Suggestions:")
            for r in other_recs[:5]:
                lines.append(f"  • {r['message']}")
        lines.append(f"\nCurrent Savings Rate: {recs['savings_rate']:.1f}%")
        return '\n'.join(lines)

    # --- Investment queries ---
    if any(w in msg for w in ['investment', 'invest', 'portfolio', 'stock', 'mutual fund', 'return']):
        inv_row = query_db(
            "SELECT COALESCE(SUM(invested_amount),0) as invested, COALESCE(SUM(current_value),0) as current FROM investments WHERE user_id=?",
            (user_id,), one=True
        )
        invested = inv_row['invested'] if inv_row else 0
        current = inv_row['current'] if inv_row else 0
        pl = current - invested
        roi = calculate_percentage(pl, invested)

        lines = ["\U0001F4C8 Investment Portfolio Summary:\n"]
        lines.append(f"Total Invested: {format_currency(invested)}")
        lines.append(f"Current Value: {format_currency(current)}")
        lines.append(f"Profit/Loss: {format_currency(pl)} ({roi:+.1f}%)\n")

        # Asset allocation
        assets = query_db(
            "SELECT asset_type, SUM(current_value) as total FROM investments WHERE user_id=? GROUP BY asset_type ORDER BY total DESC",
            (user_id,)
        )
        if assets:
            lines.append("Asset Allocation:")
            for a in assets:
                pct = calculate_percentage(a['total'], current)
                lines.append(f"  • {a['asset_type']}: {format_currency(a['total'])} ({pct:.1f}%)")

        if pl > 0:
            lines.append(f"\n✅ Your portfolio is in profit! ROI: {roi:+.1f}%")
        elif pl < 0:
            lines.append(f"\n⚠️ Your portfolio is in loss. Consider reviewing your investments.")
        return '\n'.join(lines)

    # --- Goal queries ---
    if any(w in msg for w in ['goal', 'target', 'save', 'saving goal']):
        goals = query_db("SELECT * FROM goals WHERE user_id=? ORDER BY target_date", (user_id,))
        if not goals:
            return "You haven't set any financial goals yet. Visit the Goals page to create one!"

        lines = [f"\U0001F3AF You have {len(goals)} financial goals:\n"]
        total_target = total_saved = 0
        for g in goals:
            pct = calculate_percentage(g['saved_amount'], g['target_amount'])
            lines.append(f"• {g['goal_name']}: {format_currency(g['saved_amount'])} / {format_currency(g['target_amount'])} ({pct:.0f}%)")
            total_target += g['target_amount']
            total_saved += g['saved_amount']
        lines.append(f"\nOverall Progress: {format_currency(total_saved)} / {format_currency(total_target)} "
                     f"({calculate_percentage(total_saved, total_target):.1f}%)")
        return '\n'.join(lines)

    # --- Health score ---
    if any(w in msg for w in ['health', 'score', 'financial health', 'how am i doing', 'status']):
        hs = get_health_score(user_id)
        lines = [f"\U0001F4CA Financial Health Score: {hs['score']}/100 - {hs['status']}\n"]
        lines.append("Indicators:")
        ind = hs['indicators']
        lines.append(f"  • Savings Ratio: {ind['savings_ratio']:.1f}%")
        lines.append(f"  • Expense Ratio: {ind['expense_ratio']:.1f}%")
        lines.append(f"  • Investment Growth: {ind['investment_growth']:.1f}%")
        lines.append(f"  • Debt-to-Income: {ind['debt_to_income']:.1f}%")
        lines.append(f"  • Emergency Fund: {ind['emergency_months']:.1f} months\n")
        lines.append("Recommendations:")
        for r in hs['recommendations'][:4]:
            lines.append(f"  • {r}")
        return '\n'.join(lines)

    # --- Savings ---
    if any(w in msg for w in ['saving', 'save money', 'how to save']):
        insights = get_ai_insights(user_id)
        lines = [f"\U0001F4B0 Savings Analysis:\n"]
        lines.append(f"Current Savings: {format_currency(insights['savings'])}")
        lines.append(f"Savings Rate: {insights['savings_rate']:.1f}%\n")
        saving_insights = [i for i in insights['insights'] if i['category'] in ('Savings', 'Trend')]
        for i in saving_insights:
            lines.append(f"• {i['title']}: {i['message']}")
        lines.append("\n💡 Tip: Aim to save at least 20-30% of your monthly income for financial stability.")
        return '\n'.join(lines)

    # --- Income ---
    if any(w in msg for w in ['income', 'earn', 'salary', 'earning']):
        return (f"\U0001F4B9 Your income for {summary['month_name']} {summary['year']} is {format_currency(summary['income'])}.\n"
                f"Your savings rate is {calculate_percentage(summary['savings'], summary['income']):.1f}%.\n"
                f"{'✅ Great savings rate!' if calculate_percentage(summary['savings'], summary['income']) >= 20 else '⚠️ Try to increase your savings rate.'}")

    # --- Insights / Advice ---
    if any(w in msg for w in ['advice', 'insight', 'tip', 'suggest', 'recommend', 'help', 'what should']):
        insights = get_ai_insights(user_id)
        lines = ["\U0001F4A1 AI Financial Insights:\n"]
        for i in insights['insights'][:5]:
            lines.append(f"• [{i['category']}] {i['title']}")
            lines.append(f"  {i['message']}\n")
        return '\n'.join(lines)

    # --- Report ---
    if any(w in msg for w in ['report', 'summary', 'overview', 'dashboard']):
        return (f"\U0001F4CB Financial Overview for {summary['month_name']} {summary['year']}:\n\n"
                f"• Income: {format_currency(summary['income'])}\n"
                f"• Expenses: {format_currency(summary['expense'])}\n"
                f"• Savings: {format_currency(summary['savings'])}\n"
                f"• Savings Rate: {calculate_percentage(summary['savings'], summary['income']):.1f}%\n"
                f"• Investments: {format_currency(summary['current_value'])}\n"
                f"• Goals: {summary['goals_count']}\n\n"
                f"Visit the Reports page to download detailed PDF/Excel reports.")

    # --- Thank you ---
    if any(w in msg for w in ['thank', 'thanks', 'thank you', 'bye', 'goodbye']):
        return "You're welcome! I'm always here to help with your finances. Have a great day! \U0001F64F"

    # --- Default ---
    return (f"I'm JARVIS, your AI Financial Assistant. \U0001F916\n\n"
            f"I can help you with:\n"
            f"• Expense analysis - 'Show my expenses' or 'spending breakdown'\n"
            f"• Budget recommendations - 'What's my budget?'\n"
            f"• Investment portfolio - 'How are my investments?'\n"
            f"• Financial goals - 'Show my goals'\n"
            f"• Health score - 'What's my financial health?'\n"
            f"• Savings tips - 'How can I save more?'\n"
            f"• Financial insights - 'Give me advice'\n\n"
            f"What would you like to know?")


@bp.route('/jarvis')
@login_required
def index():
    """JARVIS chatbot interface."""
    user_id = session['user_id']
    # Get conversation history
    history = query_db(
        "SELECT * FROM jarvis_chat WHERE user_id=? ORDER BY id ASC LIMIT 50",
        (user_id,)
    )
    return render_template('jarvis.html', history=history)


@bp.route('/jarvis/chat', methods=['POST'])
@login_required
def chat():
    """Handle chat message and return JARVIS response."""
    user_id = session['user_id']
    message = request.form.get('message', '').strip()

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    # Save user message
    execute_db(
        "INSERT INTO jarvis_chat (user_id, role, message) VALUES (?, ?, ?)",
        (user_id, 'user', message)
    )

    # Generate response
    response = _process_query(user_id, message)

    # Save JARVIS response
    execute_db(
        "INSERT INTO jarvis_chat (user_id, role, message) VALUES (?, ?, ?)",
        (user_id, 'assistant', response)
    )

    return jsonify({'response': response})


@bp.route('/jarvis/clear', methods=['POST'])
@login_required
def clear():
    """Clear chat history."""
    user_id = session['user_id']
    execute_db("DELETE FROM jarvis_chat WHERE user_id=?", (user_id,))
    flash('Chat history cleared.', 'success')
    return redirect(url_for('jarvis.index'))
