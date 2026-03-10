import requests
import json
from config import OLLAMA_BASE_URL, OLLAMA_MODEL
import storage


SYSTEM_PROMPT = """你是一个智能生活助手，帮助用户管理日常记录。
根据用户的消息，判断意图并返回 JSON 格式的指令。

支持的意图：
- note: 保存速记/笔记
- todo_add: 添加待办（提取 text 和可选 due 日期）
- todo_list: 查看待办列表
- todo_done: 完成待办（提取序号 id）
- finance_add: 记账（提取 amount 金额、category 分类、type: income/expense）
- finance_query: 查询收支
- habit_add: 添加习惯
- habit_checkin: 习惯打卡
- habit_list: 查看习惯
- diary_generate: 生成今日日记
- mood_query: 查看情绪
- report_weekly: 生成周报
- report_monthly: 生成月报
- chat: 普通聊天

返回格式：
{"intent": "意图名", "reply": "回复用户的文字", "data": {相关数据}}

注意：
- reply 必须是简短友好的中文回复
- 只返回 JSON，不要有其他内容
"""


def call_ollama(messages):
    """调用 Ollama API"""
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "format": "json",
    }
    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        content = result.get("message", {}).get("content", "{}")
        return json.loads(content)
    except Exception as e:
        return {"intent": "chat", "reply": f"AI 暂时无法响应：{e}", "data": {}}


def process_message(user_id, text):
    """处理文字消息，返回回复文本"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]
    result = call_ollama(messages)
    intent = result.get("intent", "chat")
    reply = result.get("reply", "已收到")
    data = result.get("data", {})

    # 根据意图执行操作
    if intent == "note":
        storage.save_note(user_id, text)
    elif intent == "todo_add":
        todo_text = data.get("text", text)
        due = data.get("due")
        storage.add_todo(user_id, todo_text, due)
    elif intent == "todo_list":
        todos = storage.get_todos(user_id)
        undone = [t for t in todos if not t["done"]]
        if undone:
            lines = [f"{i+1}. {t['text']}" + (f"（截止：{t['due']}）" if t.get("due") else "") for i, t in enumerate(undone)]
            reply = "📋 待办列表：\n" + "\n".join(lines)
        else:
            reply = "✅ 没有待办事项"
    elif intent == "todo_done":
        todo_id = data.get("id", 1)
        todos = storage.get_todos(user_id)
        undone = [t for t in todos if not t["done"]]
        if 0 < todo_id <= len(undone):
            undone[todo_id - 1]["done"] = True
            storage.save_todos(user_id, todos)
            reply = f"✅ 已完成：{undone[todo_id-1]['text']}"
    elif intent == "finance_add":
        amount = data.get("amount", 0)
        category = data.get("category", "其他")
        note = data.get("note", text)
        ftype = data.get("type", "expense")
        storage.add_finance(user_id, amount, category, note, ftype)
    elif intent == "finance_query":
        records = storage.get_finance(user_id)
        if records:
            total_expense = sum(r["amount"] for r in records if r["type"] == "expense")
            total_income = sum(r["amount"] for r in records if r["type"] == "income")
            reply = f"💰 收支统计：\n收入：¥{total_income:.2f}\n支出：¥{total_expense:.2f}\n结余：¥{total_income - total_expense:.2f}"
        else:
            reply = "暂无收支记录"
    elif intent == "habit_add":
        habits = storage.get_habits(user_id)
        habit_name = data.get("name", text)
        habits.append({"id": len(habits)+1, "name": habit_name, "checkins": []})
        storage.save_habits(user_id, habits)
    elif intent == "habit_checkin":
        import datetime
        habits = storage.get_habits(user_id)
        today = datetime.date.today().isoformat()
        habit_id = data.get("id", 1)
        for h in habits:
            if h["id"] == habit_id:
                if today not in h.get("checkins", []):
                    h.setdefault("checkins", []).append(today)
                    reply = f"✅ 习惯打卡成功：{h['name']}"
                else:
                    reply = f"今天已经打卡过了：{h['name']}"
                break
        storage.save_habits(user_id, habits)
    elif intent == "habit_list":
        import datetime
        habits = storage.get_habits(user_id)
        today = datetime.date.today().isoformat()
        if habits:
            lines = []
            for h in habits:
                checked = "✅" if today in h.get("checkins", []) else "⬜"
                lines.append(f"{checked} {h['name']}（连续{len(h.get('checkins',[]))}天）")
            reply = "🎯 习惯追踪：\n" + "\n".join(lines)
        else:
            reply = "还没有设定习惯，发送「添加习惯 xxx」来设定"
    elif intent == "diary_generate":
        reply = generate_diary(user_id)
    elif intent == "mood_query":
        import datetime
        mood = storage.get_mood(user_id)
        if mood:
            reply = f"今日情绪：{mood['score']}/10\n{mood['summary']}"
        else:
            reply = "今日暂无情绪记录"

    # 每条消息都自动保存速记
    if intent not in ("todo_list", "finance_query", "habit_list", "mood_query"):
        storage.save_note(user_id, text)

    return reply


def process_image_message(user_id, image_path, caption=""):
    """处理图片消息"""
    storage.save_note(user_id, caption or "[图片]", image_paths=[image_path])
    return "📷 图片已保存"


def generate_diary(user_id):
    """生成今日日记"""
    import datetime
    today = datetime.date.today().isoformat()
    notes = storage.get_notes(user_id, today)
    if not notes:
        return "今天还没有记录，发点什么吧～"

    note_texts = "\n".join([n["content"] for n in notes if n["content"] != "[图片]"])
    messages = [
        {"role": "system", "content": "你是一个日记生成助手，根据用户今天的碎片记录，生成一篇温暖自然的日记。只返回日记正文，200字左右。"},
        {"role": "user", "content": f"今天的记录：\n{note_texts}"},
    ]
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {"model": OLLAMA_MODEL, "messages": messages, "stream": False}
    try:
        resp = requests.post(url, json=payload, timeout=60)
        content = resp.json().get("message", {}).get("content", "")
        storage.save_diary(user_id, content)
        return f"📔 今日日记已生成：\n\n{content}"
    except Exception as e:
        return f"日记生成失败：{e}"


def generate_report(user_id, report_type="weekly"):
    """生成周报/月报"""
    import datetime
    notes = storage.get_notes(user_id)
    if not notes:
        return "暂无足够数据生成报告"

    note_texts = "\n".join([f"{n.get('date','')} {n['content']}" for n in notes[:50] if n["content"] != "[图片]"])
    report_name = "周报" if report_type == "weekly" else "月报"
    messages = [
        {"role": "system", "content": f"你是一个总结助手，根据用户的记录生成{report_name}，包括：本周/月亮点、完成的事、情绪状态、下周/月计划。300字左右。"},
        {"role": "user", "content": f"记录如下：\n{note_texts}"},
    ]
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {"model": OLLAMA_MODEL, "messages": messages, "stream": False}
    try:
        resp = requests.post(url, json=payload, timeout=60)
        content = resp.json().get("message", {}).get("content", "")
        return f"📊 {report_name}：\n\n{content}"
    except Exception as e:
        return f"{report_name}生成失败：{e}"
