import os
import sys
import time
import hashlib
import xml.etree.ElementTree as ET
import requests
from flask import Flask, request, jsonify

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    WEWORK_TOKEN, WEWORK_ENCODING_AES_KEY, WEWORK_CORP_ID,
    WEWORK_CORP_SECRET, WEWORK_AGENT_ID, DEFAULT_USER_ID,
    SERVER_PORT, DATA_DIR, ADMIN_TOKEN
)
from wework_crypto import WeworkCrypto
import brain
import storage
from web_routes import web
from scheduler import start_scheduler

app = Flask(__name__)
app.register_blueprint(web)

crypto = WeworkCrypto(WEWORK_TOKEN, WEWORK_ENCODING_AES_KEY, WEWORK_CORP_ID)

_access_token_cache = {"token": "", "expires": 0}

def get_access_token():
    if time.time() < _access_token_cache["expires"]:
        return _access_token_cache["token"]
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={WEWORK_CORP_ID}&corpsecret={WEWORK_CORP_SECRET}"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    token = data.get("access_token", "")
    _access_token_cache["token"] = token
    _access_token_cache["expires"] = time.time() + 7000
    return token


def send_text(user_id, content):
    token = get_access_token()
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
    payload = {
        "touser": user_id,
        "msgtype": "text",
        "agentid": WEWORK_AGENT_ID,
        "text": {"content": content},
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[SendMsg] 失败: {e}")


def download_image(media_id, user_id):
    """下载企微图片到本地"""
    token = get_access_token()
    url = f"https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token={token}&media_id={media_id}"
    try:
        resp = requests.get(url, timeout=30, stream=True)
        if resp.status_code == 200:
            content_type = resp.headers.get("Content-Type", "image/jpeg")
            ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]
            filename = f"{media_id}.{ext}"
            images_dir = storage.get_images_dir(user_id)
            filepath = os.path.join(images_dir, filename)
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            return filepath
    except Exception as e:
        print(f"[DownloadImage] 失败: {e}")
    return None


@app.route("/wework", methods=["GET", "POST"])
def wework():
    msg_signature = request.args.get("msg_signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")

    # GET：验证回调 URL
    if request.method == "GET":
        echo_str = request.args.get("echostr", "")
        if crypto.verify_signature(msg_signature, timestamp, nonce, echo_str):
            decrypted = crypto.decrypt(echo_str)
            return decrypted
        return "验证失败", 403

    # POST：处理消息
    try:
        xml_str = crypto.decrypt(
            ET.fromstring(request.data).find("Encrypt").text
        )
        msg = WeworkCrypto.parse_xml(xml_str)
        user_id = msg.get("FromUserName", DEFAULT_USER_ID)
        msg_type = msg.get("MsgType", "text")

        if msg_type == "text":
            text = msg.get("Content", "")
            reply = brain.process_message(user_id, text)
            send_text(user_id, reply)

        elif msg_type == "image":
            media_id = msg.get("MediaId", "")
            filepath = download_image(media_id, user_id)
            if filepath:
                reply = brain.process_image_message(user_id, filepath)
            else:
                reply = "图片保存失败，请重试"
            send_text(user_id, reply)

        elif msg_type == "voice":
            # 语音消息：尝试获取识别文字
            recognition = msg.get("Recognition", "")
            if recognition:
                reply = brain.process_message(user_id, f"[语音] {recognition}")
            else:
                reply = "已收到语音，暂不支持语音识别"
                storage.save_note(user_id, "[语音消息]")
            send_text(user_id, reply)

    except Exception as e:
        print(f"[Wework] 处理消息失败: {e}")

    return "success"


@app.route("/api/verify", methods=["POST"])
def api_verify():
    data = request.get_json()
    if data.get("password") == ADMIN_TOKEN:
        import secrets
        token = secrets.token_urlsafe(32)
        return jsonify({"ok": True, "token": token})
    return jsonify({"ok": False})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    start_scheduler()
    print(f"[MyAssistant] 启动在端口 {SERVER_PORT}")
    app.run(host="0.0.0.0", port=SERVER_PORT, debug=False)
