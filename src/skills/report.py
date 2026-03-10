"""
周报/月报生成模块
"""
from datetime import date
import storage


def generate(user_id: str, report_type: str, brain) -> str:
    """生成周报或月报"""
    if report_type == 'week':
        messages = storage.get_week_messages(user_id)
        period_name = '周报'
        date_range = _get_week_range()
    else:
        month = date.today().strftime('%Y-%m')
        messages = storage.get_month_messages(user_id, month)
        period_name = '月报'
        date_range = month

    if not messages:
        return f"📊 暂无数据，无法生成{period_name}"

    messages_text = '\n'.join([
        f"[{m.get('time', '')[:10]}] {m.get('content', '')}"
        for m in messages
        if m.get('content')
    ])

    try:
        report = brain.generate_report(messages_text, report_type)
        return f"📊 **{date_range} {period_name}**\n\n{report}"
    except RuntimeError as e:
        return str(e)


def _get_week_range() -> str:
    """获取本周日期范围"""
    from datetime import timedelta
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return f"{start.strftime('%Y/%m/%d')}-{end.strftime('%m/%d')}"
