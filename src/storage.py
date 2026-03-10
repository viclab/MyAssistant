import os
import json
import datetime
from config import DATA_DIR


def get_user_dir(user_id):
    path = os.path.join(DATA_DIR, "users", user_id)
    os.makedirs(path, exist_ok=True)
    return path


def get_images_dir(user_id):
    path = os.path.join(get_user_dir(user_id), "images")
    os.makedirs(path, exist_ok=True)
    return path


def save_note(user_id, content, image_paths=None):
    """保存速记（文字+图片）"""
    today = datetime.date.today().isoformat()
    notes_dir = os.path.join(get_user_dir(user_id), "notes")
    os.makedirs(notes_dir, exist_ok=True)
    filepath = os.path.join(notes_dir, f"{today}.json")

    notes = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            notes = json.load(f)

    note = {
        "id": len(notes) + 1,
        "time": datetime.datetime.now().isoformat(),
        "content": content,
        "images": image_paths or [],
    }
    notes.append(note)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    return note


def get_notes(user_id, date=None):
    """获取速记列表"""
    notes_dir = os.path.join(get_user_dir(user_id), "notes")
    if not os.path.exists(notes_dir):
        return []

    if date:
        filepath = os.path.join(notes_dir, f"{date}.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    # 返回最近7天
    all_notes = []
    for filename in sorted(os.listdir(notes_dir), reverse=True)[:7]:
        if filename.endswith(".json"):
            with open(os.path.join(notes_dir, filename), "r", encoding="utf-8") as f:
                day_notes = json.load(f)
                for n in day_notes:
                    n["date"] = filename.replace(".json", "")
                all_notes.extend(day_notes)
    return all_notes


def get_todos(user_id):
    filepath = os.path.join(get_user_dir(user_id), "todos.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_todos(user_id, todos):
    filepath = os.path.join(get_user_dir(user_id), "todos.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def add_todo(user_id, text, due=None):
    todos = get_todos(user_id)
    todo = {
        "id": len(todos) + 1,
        "text": text,
        "done": False,
        "created": datetime.datetime.now().isoformat(),
        "due": due,
    }
    todos.append(todo)
    save_todos(user_id, todos)
    return todo


def get_diary(user_id, date=None):
    today = date or datetime.date.today().isoformat()
    diary_dir = os.path.join(get_user_dir(user_id), "diary")
    os.makedirs(diary_dir, exist_ok=True)
    filepath = os.path.join(diary_dir, f"{today}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_diary(user_id, content, date=None):
    today = date or datetime.date.today().isoformat()
    diary_dir = os.path.join(get_user_dir(user_id), "diary")
    os.makedirs(diary_dir, exist_ok=True)
    filepath = os.path.join(diary_dir, f"{today}.json")
    diary = {
        "date": today,
        "content": content,
        "created": datetime.datetime.now().isoformat(),
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(diary, f, ensure_ascii=False, indent=2)
    return diary


def get_finance(user_id):
    filepath = os.path.join(get_user_dir(user_id), "finance.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def add_finance(user_id, amount, category, note="", type_="expense"):
    records = get_finance(user_id)
    record = {
        "id": len(records) + 1,
        "type": type_,
        "amount": amount,
        "category": category,
        "note": note,
        "time": datetime.datetime.now().isoformat(),
    }
    records.append(record)
    filepath = os.path.join(get_user_dir(user_id), "finance.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    return record


def get_habits(user_id):
    filepath = os.path.join(get_user_dir(user_id), "habits.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_habits(user_id, habits):
    filepath = os.path.join(get_user_dir(user_id), "habits.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(habits, f, ensure_ascii=False, indent=2)


def get_mood(user_id, date=None):
    today = date or datetime.date.today().isoformat()
    mood_dir = os.path.join(get_user_dir(user_id), "mood")
    os.makedirs(mood_dir, exist_ok=True)
    filepath = os.path.join(mood_dir, f"{today}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_mood(user_id, score, summary, date=None):
    today = date or datetime.date.today().isoformat()
    mood_dir = os.path.join(get_user_dir(user_id), "mood")
    os.makedirs(mood_dir, exist_ok=True)
    filepath = os.path.join(mood_dir, f"{today}.json")
    mood = {
        "date": today,
        "score": score,
        "summary": summary,
        "created": datetime.datetime.now().isoformat(),
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(mood, f, ensure_ascii=False, indent=2)
    return mood
