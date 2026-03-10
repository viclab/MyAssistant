"""
速记功能模块
"""
from typing import List
import storage


def handle(user_id: str, content: str, image_paths: List[str],
           brain, silent: bool = False) -> str:
    """处理速记消息"""
    msg_type = 'image' if image_paths else 'text'
    entry = storage.save_note(user_id, content, image_paths, msg_type)

    if silent:
        return ''

    if image_paths:
        return f"📷 已保存图片笔记（{len(image_paths)} 张图片）\n时间：{entry['time']}"
    else:
        preview = content[:30] + '...' if len(content) > 30 else content
        return f"📝 已记录：{preview}\n时间：{entry['time']}"
