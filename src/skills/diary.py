"""
日记生成模块
"""
from datetime import date
import storage


def generate(user_id: str, brain) -> str:
    """生成今日日记"""
    today = date.today().strftime('%Y-%m-%d')
    notes = storage.get_notes(user_id, today)

    if not notes:
        return "📖 今天还没有记录，先去聊聊天或记点什么吧～"

    # 整理今天的消息文本
    messages_text = '\n'.join([
        f"[{n['time'][11:16]}] {n['content']}"
        for n in notes
        if n.get('content')
    ])

    try:
        diary_content = brain.generate_diary(messages_text)
        storage.save_diary(user_id, diary_content, today)
        return f"📖 **{today} 日记**\n\n{diary_content}"
    except RuntimeError as e:
        return str(e)


def get_diary_entry(user_id: str, target_date: str = None) -> str:
    """获取日记"""
    diary = storage.get_diary(user_id, target_date)
    if not diary:
        d = target_date or date.today().strftime('%Y-%m-%d')
        return f"📖 {d} 还没有日记"
    return f"📖 **{diary['date']} 日记**\n\n{diary['content']}"
