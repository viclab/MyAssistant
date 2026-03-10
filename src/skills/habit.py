"""
习惯追踪模块
"""
import storage


def add(user_id: str, habit_name: str) -> str:
    """添加习惯"""
    if not habit_name:
        return "🎯 请告诉我要养成什么习惯，例如：每天喝 8 杯水"
    habit = storage.add_habit(user_id, habit_name)
    return f"🎯 习惯已设置：{habit_name}\n每天打卡提醒已开启，加油！💪"


def checkin(user_id: str, keyword: str) -> str:
    """打卡"""
    result = storage.checkin_habit(user_id, keyword)
    if not result:
        habits = storage.get_habits(user_id)
        if not habits:
            return "🎯 你还没有设置习惯，先设置一个吧！"
        names = '、'.join(h['name'] for h in habits[:5])
        return f"🔍 没找到习惯「{keyword}」\n你的习惯：{names}"

    checkins = result.get('checkins', [])
    streak = len([c for c in sorted(checkins, reverse=True)[:30]])  # 简化计算
    return f"✅ 打卡成功：{result['name']}\n🔥 已坚持 {len(checkins)} 天"


def list_habits(user_id: str) -> str:
    """列出习惯"""
    stats = storage.get_habit_stats(user_id)
    if not stats:
        return "🎯 还没有习惯目标，试试说「每天早起」或「坚持运动」来设定习惯吧！"

    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    lines = ["🎯 **我的习惯**\n"]
    for h in stats:
        done = '✅' if h.get('today_done') else '⬜'
        streak = h.get('streak', 0)
        monthly = h.get('monthly_count', 0)
        fire = '🔥' if streak >= 3 else ''
        lines.append(
            f"{done} {h['name']} {fire}\n"
            f"   连续 {streak} 天 · 本月 {monthly} 次"
        )

    return '\n'.join(lines)
