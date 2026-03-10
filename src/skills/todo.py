"""
待办管理模块
"""
import storage


def add(user_id: str, content: str, due_date: str = None) -> str:
    """添加待办"""
    todo = storage.add_todo(user_id, content, due_date)
    due_str = f"\n⏰ 截止：{due_date}" if due_date else ""
    return f"✅ 已添加待办：{content}{due_str}"


def complete(user_id: str, keyword: str) -> str:
    """完成待办"""
    todos = storage.get_todos(user_id)
    matched = [t for t in todos if not t['done'] and keyword in t['content']]
    if not matched:
        return f"🔍 没有找到包含「{keyword}」的待办"
    # 完成第一个匹配项
    todo = matched[0]
    storage.complete_todo(user_id, todo['id'])
    return f"🎉 已完成：{todo['content']}"


def delete(user_id: str, keyword: str) -> str:
    """删除待办"""
    todos = storage.get_todos(user_id)
    matched = [t for t in todos if keyword in t['content']]
    if not matched:
        return f"🔍 没有找到包含「{keyword}」的待办"
    todo = matched[0]
    storage.delete_todo(user_id, todo['id'])
    return f"🗑️ 已删除：{todo['content']}"


def list_todos(user_id: str) -> str:
    """列出待办"""
    todos = storage.get_todos(user_id)
    if not todos:
        return "📋 待办列表为空，快去添加任务吧！"

    pending = [t for t in todos if not t['done']]
    done = [t for t in todos if t['done']]

    lines = ["📋 **待办列表**\n"]
    if pending:
        lines.append("未完成：")
        for i, t in enumerate(pending, 1):
            due = f" (截止 {t['due_date']})" if t.get('due_date') else ""
            lines.append(f"  {i}. ⬜ {t['content']}{due}")
    else:
        lines.append("✨ 所有任务已完成！")

    if done:
        lines.append(f"\n已完成（{len(done)} 项）：")
        for t in done[-3:]:  # 只显示最近 3 个
            lines.append(f"  ✅ {t['content']}")

    return '\n'.join(lines)
