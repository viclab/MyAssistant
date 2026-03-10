from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import brain
import storage
from config import DEFAULT_USER_ID, WEWORK_CORP_ID, WEWORK_AGENT_ID, WEWORK_CORP_SECRET
import requests


def get_access_token():
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={WEWORK_CORP_ID}&corpsecret={WEWORK_CORP_SECRET}"
    resp = requests.get(url, timeout=10)
    return resp.json().get("access_token", "")


def send_wework_msg(user_id, content):
    token = get_access_token()
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
    payload = {
        "touser": user_id,
        "msgtype": "text",
        "agentid": WEWORK_AGENT_ID,
        "text": {"content": content},
    }
    requests.post(url, json=payload, timeout=10)


def daily_diary_job():
    """每天22:30自动生成日记并推送"""
    if not DEFAULT_USER_ID:
        return
    try:
        diary = brain.generate_diary(DEFAULT_USER_ID)
        send_wework_msg(DEFAULT_USER_ID, diary)
    except Exception as e:
        print(f"[Scheduler] 日记生成失败: {e}")


def weekly_report_job():
    """每周日21:00生成周报"""
    if not DEFAULT_USER_ID:
        return
    try:
        report = brain.generate_report(DEFAULT_USER_ID, "weekly")
        send_wework_msg(DEFAULT_USER_ID, report)
    except Exception as e:
        print(f"[Scheduler] 周报生成失败: {e}")


def monthly_report_job():
    """每月末22:00生成月报"""
    if not DEFAULT_USER_ID:
        return
    try:
        report = brain.generate_report(DEFAULT_USER_ID, "monthly")
        send_wework_msg(DEFAULT_USER_ID, report)
    except Exception as e:
        print(f"[Scheduler] 月报生成失败: {e}")


def mood_analysis_job():
    """每天22:00情绪分析"""
    if not DEFAULT_USER_ID:
        return
    try:
        import datetime
        today = datetime.date.today().isoformat()
        notes = storage.get_notes(DEFAULT_USER_ID, today)
        if not notes:
            return
        import requests as req
        from config import OLLAMA_BASE_URL, OLLAMA_MODEL
        texts = "\n".join([n["content"] for n in notes if n["content"] != "[图片]"])
        messages = [
            {"role": "system", "content": "分析以下今日记录中的情绪状态，给出1-10分评分（10最积极），和一句话总结。返回JSON: {\"score\": 数字, \"summary\": \"总结\"}"},
            {"role": "user", "content": texts},
        ]
        import json
        resp = req.post(f"{OLLAMA_BASE_URL}/api/chat", json={"model": OLLAMA_MODEL, "messages": messages, "stream": False, "format": "json"}, timeout=60)
        data = json.loads(resp.json().get("message", {}).get("content", "{}"))
        storage.save_mood(DEFAULT_USER_ID, data.get("score", 5), data.get("summary", ""))
    except Exception as e:
        print(f"[Scheduler] 情绪分析失败: {e}")


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(daily_diary_job, "cron", hour=22, minute=30)
    scheduler.add_job(weekly_report_job, "cron", day_of_week="sun", hour=21, minute=0)
    scheduler.add_job(monthly_report_job, "cron", day="last", hour=22, minute=0)
    scheduler.add_job(mood_analysis_job, "cron", hour=22, minute=0)
    scheduler.start()
    print("[Scheduler] 定时任务已启动")
    return scheduler
