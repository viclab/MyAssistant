"""
情绪分析模块
"""
import storage

MOOD_EMOJI = {
    '开心': '😊', '平静': '😌', '焦虑': '😰',
    '难过': '😢', '愤怒': '😠', '疲惫': '😴', '兴奋': '🤩',
}


def handle(user_id: str, message: str, brain) -> str:
    """处理情绪消息"""
    try:
        result = brain.analyze_mood(message)
        mood = result.get('mood', '平静')
        score = result.get('score', 5.0)
        analysis = result.get('analysis', '')

        entry = storage.save_mood(user_id, mood, score, analysis, message)
        emoji = MOOD_EMOJI.get(mood, '💭')

        return (
            f"{emoji} 情绪记录\n"
            f"心情：{mood}（{score:.0f}/10）\n"
            f"分析：{analysis}"
        )
    except RuntimeError as e:
        return str(e)


def get_mood_summary(user_id: str, days: int = 7) -> str:
    """获取情绪摘要"""
    records = storage.get_mood_records(user_id, days)
    if not records:
        return f"📊 最近 {days} 天没有情绪记录"

    total = len(records)
    avg_score = sum(r.get('score', 5) for r in records) / total
    mood_counts = {}
    for r in records:
        m = r.get('mood', '平静')
        mood_counts[m] = mood_counts.get(m, 0) + 1

    most_mood = max(mood_counts, key=mood_counts.get)
    emoji = MOOD_EMOJI.get(most_mood, '💭')

    lines = [
        f"📊 最近 {days} 天情绪报告",
        f"共 {total} 条记录",
        f"平均心情指数：{avg_score:.1f}/10",
        f"最多情绪：{emoji}{most_mood}",
        "各情绪分布："
    ]
    for mood, count in sorted(mood_counts.items(), key=lambda x: -x[1]):
        e = MOOD_EMOJI.get(mood, '💭')
        lines.append(f"  {e}{mood}: {count}次")

    return '\n'.join(lines)
