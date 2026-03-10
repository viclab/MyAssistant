import os
import json
import datetime
from flask import Blueprint, jsonify, request, send_file, render_template_string
import storage
from config import DATA_DIR, ADMIN_TOKEN, WEB_DOMAIN

web = Blueprint("web", __name__)

# ==================== API ====================

@web.route("/api/notes")
def api_notes():
    user_id = request.args.get("user_id", "default")
    date = request.args.get("date")
    notes = storage.get_notes(user_id, date)
    return jsonify(notes)


@web.route("/api/todos")
def api_todos():
    user_id = request.args.get("user_id", "default")
    todos = storage.get_todos(user_id)
    return jsonify(todos)


@web.route("/api/diary")
def api_diary():
    user_id = request.args.get("user_id", "default")
    date = request.args.get("date", datetime.date.today().isoformat())
    diary = storage.get_diary(user_id, date)
    return jsonify(diary or {})


@web.route("/api/finance")
def api_finance():
    user_id = request.args.get("user_id", "default")
    records = storage.get_finance(user_id)
    return jsonify(records)


@web.route("/api/habits")
def api_habits():
    user_id = request.args.get("user_id", "default")
    habits = storage.get_habits(user_id)
    return jsonify(habits)


@web.route("/api/mood")
def api_mood():
    user_id = request.args.get("user_id", "default")
    # 返回最近7天情绪
    mood_dir = os.path.join(DATA_DIR, "users", user_id, "mood")
    moods = []
    if os.path.exists(mood_dir):
        for filename in sorted(os.listdir(mood_dir), reverse=True)[:7]:
            if filename.endswith(".json"):
                with open(os.path.join(mood_dir, filename), "r", encoding="utf-8") as f:
                    moods.append(json.load(f))
    return jsonify(moods)


@web.route("/api/image/<user_id>/<filename>")
def api_image(user_id, filename):
    images_dir = storage.get_images_dir(user_id)
    filepath = os.path.join(images_dir, filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    return "Not found", 404


# ==================== Web 页面 ====================

@web.route("/web/login")
def web_login():
    token = request.args.get("token", "")
    return render_template_string(LOGIN_HTML, token=token, domain=WEB_DOMAIN)


@web.route("/web/index")
def web_index():
    return render_template_string(INDEX_HTML, domain=WEB_DOMAIN)


@web.route("/web/notes")
def web_notes():
    return render_template_string(NOTES_HTML, domain=WEB_DOMAIN)


@web.route("/web/todos")
def web_todos():
    return render_template_string(TODOS_HTML, domain=WEB_DOMAIN)


@web.route("/web/diary")
def web_diary():
    return render_template_string(DIARY_HTML, domain=WEB_DOMAIN)


@web.route("/web/finance")
def web_finance():
    return render_template_string(FINANCE_HTML, domain=WEB_DOMAIN)


@web.route("/web/habits")
def web_habits():
    return render_template_string(HABITS_HTML, domain=WEB_DOMAIN)


@web.route("/web/mood")
def web_mood():
    return render_template_string(MOOD_HTML, domain=WEB_DOMAIN)


# ==================== HTML 模板 ====================

NAV_HTML = """
<nav style="position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #eee;display:flex;justify-content:space-around;padding:8px 0;z-index:100;box-shadow:0 -2px 10px rgba(0,0,0,0.05)">
  <a href="/web/index" style="text-decoration:none;color:#666;text-align:center;font-size:12px"><div style="font-size:20px">🏠</div>首页</a>
  <a href="/web/notes" style="text-decoration:none;color:#666;text-align:center;font-size:12px"><div style="font-size:20px">📝</div>速记</a>
  <a href="/web/todos" style="text-decoration:none;color:#666;text-align:center;font-size:12px"><div style="font-size:20px">✅</div>待办</a>
  <a href="/web/diary" style="text-decoration:none;color:#666;text-align:center;font-size:12px"><div style="font-size:20px">📔</div>日记</a>
  <a href="/web/mood" style="text-decoration:none;color:#666;text-align:center;font-size:12px"><div style="font-size:20px">😊</div>情绪</a>
</nav>
"""

BASE_CSS = """
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif; background: #f5f5f7; color: #333; padding-bottom: 70px; }
.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px 16px 16px; }
.header h1 { font-size: 20px; font-weight: 600; }
.header p { font-size: 13px; opacity: 0.8; margin-top: 4px; }
.card { background: white; border-radius: 12px; margin: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.tag { display:inline-block; background:#f0f0f5; border-radius:20px; padding:2px 10px; font-size:12px; color:#666; margin:2px; }
.btn { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 8px; padding: 10px 20px; cursor: pointer; font-size: 14px; }
</style>
"""

LOGIN_HTML = BASE_CSS + """
<div class="header"><h1>🤖 我的助手</h1><p>请验证身份</p></div>
<div class="card" style="margin-top:20px">
  <p style="color:#666;margin-bottom:16px">输入访问密码：</p>
  <input id="pwd" type="password" placeholder="访问密码" style="width:100%;border:1px solid #ddd;border-radius:8px;padding:10px;font-size:14px;margin-bottom:12px">
  <button class="btn" style="width:100%" onclick="login()">进入</button>
</div>
<script>
// 如果有 token 参数直接存储
const urlToken = "{{ token }}";
if(urlToken) { localStorage.setItem("token", urlToken); }

function login() {
  const pwd = document.getElementById("pwd").value;
  fetch("/api/verify", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({password: pwd})})
    .then(r => r.json()).then(d => {
      if(d.ok) { localStorage.setItem("token", d.token); window.location="/web/index"; }
      else { alert("密码错误"); }
    });
}
if(urlToken) window.location="/web/index";
</script>
""" + NAV_HTML

INDEX_HTML = BASE_CSS + """
<div class="header"><h1>🏠 今日概览</h1><p id="dateStr"></p></div>
<div id="stats" style="display:flex;gap:8px;padding:12px;overflow-x:auto"></div>
<div class="card"><h3 style="margin-bottom:12px;font-size:15px">📋 待办</h3><div id="todos"></div></div>
<div class="card"><h3 style="margin-bottom:12px;font-size:15px">📝 最近速记</h3><div id="recent-notes"></div></div>
<script>
const uid = localStorage.getItem("uid") || "default";
document.getElementById("dateStr").textContent = new Date().toLocaleDateString("zh-CN", {year:"numeric",month:"long",day:"numeric",weekday:"long"});

fetch(`/api/todos?user_id=${uid}`).then(r=>r.json()).then(data => {
  const undone = data.filter(t=>!t.done).slice(0,5);
  document.getElementById("todos").innerHTML = undone.length
    ? undone.map(t=>`<div style="padding:8px 0;border-bottom:1px solid #f5f5f5;font-size:14px">⬜ ${t.text}${t.due?`<span style="color:#999;font-size:12px"> · ${t.due}</span>`:""}</div>`).join("")
    : `<p style="color:#999;font-size:14px">暂无待办 🎉</p>`;
});

fetch(`/api/notes?user_id=${uid}`).then(r=>r.json()).then(data => {
  const recent = data.slice(-3).reverse();
  document.getElementById("recent-notes").innerHTML = recent.length
    ? recent.map(n=>`<div style="padding:8px 0;border-bottom:1px solid #f5f5f5">
        <p style="font-size:14px">${n.content}</p>
        ${n.images&&n.images.length?`<img src="/api/image/${uid}/${n.images[0].split('/').pop()}" style="max-width:100%;border-radius:8px;margin-top:6px">`:""}
        <p style="font-size:12px;color:#999;margin-top:4px">${new Date(n.time).toLocaleTimeString("zh-CN",{hour:"2-digit",minute:"2-digit"})}</p>
      </div>`).join("")
    : `<p style="color:#999;font-size:14px">今天还没有记录</p>`;
});
</script>
""" + NAV_HTML

NOTES_HTML = BASE_CSS + """
<style>
.masonry { columns: 2; gap: 10px; padding: 12px; }
.note-card { break-inside: avoid; background: white; border-radius: 12px; margin-bottom: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.note-card img { width: 100%; display: block; }
.note-card .text { padding: 10px 12px; }
.note-card .time { font-size: 11px; color: #999; margin-top: 4px; }
</style>
<div class="header">
  <h1>📝 速记</h1>
  <p>图文并茂，记录生活</p>
</div>
<div style="padding:12px">
  <input type="date" id="dateFilter" style="width:100%;border:1px solid #ddd;border-radius:8px;padding:8px;font-size:14px" onchange="loadNotes()">
</div>
<div class="masonry" id="notes-container"></div>
<script>
const uid = localStorage.getItem("uid") || "default";
document.getElementById("dateFilter").value = new Date().toISOString().split("T")[0];

function loadNotes() {
  const date = document.getElementById("dateFilter").value;
  fetch(`/api/notes?user_id=${uid}&date=${date}`).then(r=>r.json()).then(data => {
    const container = document.getElementById("notes-container");
    if(!data.length) { container.innerHTML = `<p style="color:#999;padding:20px;text-align:center">这天没有记录</p>`; return; }
    container.innerHTML = data.reverse().map(n => {
      const imgs = (n.images||[]).map(img => `<img src="/api/image/${uid}/${img.split('/').pop()}" loading="lazy">`).join("");
      const time = new Date(n.time).toLocaleTimeString("zh-CN",{hour:"2-digit",minute:"2-digit"});
      return `<div class="note-card">
        ${imgs}
        <div class="text">
          ${n.content && n.content!=="[图片]" ? `<p style="font-size:14px;line-height:1.5">${n.content}</p>` : ""}
          <div class="time">${time}</div>
        </div>
      </div>`;
    }).join("");
  });
}
loadNotes();
</script>
""" + NAV_HTML

TODOS_HTML = BASE_CSS + """
<div class="header"><h1>✅ 待办</h1><p>管理你的任务清单</p></div>
<div class="card">
  <div id="todo-list"></div>
</div>
<script>
const uid = localStorage.getItem("uid") || "default";
fetch(`/api/todos?user_id=${uid}`).then(r=>r.json()).then(data => {
  const undone = data.filter(t=>!t.done);
  const done = data.filter(t=>t.done);
  let html = "";
  if(undone.length) {
    html += undone.map((t,i) => `<div style="display:flex;align-items:center;padding:12px 0;border-bottom:1px solid #f5f5f5">
      <span style="font-size:20px;margin-right:10px">⬜</span>
      <div style="flex:1"><p style="font-size:14px">${t.text}</p>${t.due?`<p style="font-size:12px;color:#999">${t.due}</p>`:""}</div>
    </div>`).join("");
  }
  if(done.length) {
    html += `<p style="font-size:12px;color:#999;margin:12px 0 6px">已完成 (${done.length})</p>`;
    html += done.map(t=>`<div style="padding:8px 0;border-bottom:1px solid #f5f5f5;opacity:0.5">
      <span style="font-size:14px;text-decoration:line-through">✅ ${t.text}</span>
    </div>`).join("");
  }
  document.getElementById("todo-list").innerHTML = html || `<p style="color:#999;text-align:center;padding:20px">没有待办，去聊天添加吧～</p>`;
});
</script>
""" + NAV_HTML

DIARY_HTML = BASE_CSS + """
<div class="header"><h1>📔 日记</h1><p>AI 为你整理每一天</p></div>
<div style="padding:12px"><input type="date" id="dateFilter" style="width:100%;border:1px solid #ddd;border-radius:8px;padding:8px;font-size:14px" onchange="loadDiary()"></div>
<div class="card" id="diary-content"><p style="color:#999;text-align:center;padding:20px">加载中...</p></div>
<script>
const uid = localStorage.getItem("uid") || "default";
document.getElementById("dateFilter").value = new Date().toISOString().split("T")[0];
function loadDiary() {
  const date = document.getElementById("dateFilter").value;
  fetch(`/api/diary?user_id=${uid}&date=${date}`).then(r=>r.json()).then(data => {
    document.getElementById("diary-content").innerHTML = data.content
      ? `<h3 style="color:#667eea;margin-bottom:12px">${data.date}</h3><p style="line-height:1.8;font-size:15px">${data.content.replace(/\\n/g,"<br>")}</p>`
      : `<p style="color:#999;text-align:center;padding:20px">这天还没有日记<br><small>发送「生成今日日记」让 AI 帮你整理</small></p>`;
  });
}
loadDiary();
</script>
""" + NAV_HTML

FINANCE_HTML = BASE_CSS + """
<div class="header"><h1>💰 财务</h1><p>收支一目了然</p></div>
<div id="summary" style="display:flex;gap:10px;padding:12px"></div>
<div class="card"><h3 style="margin-bottom:12px;font-size:15px">明细记录</h3><div id="records"></div></div>
<script>
const uid = localStorage.getItem("uid") || "default";
fetch(`/api/finance?user_id=${uid}`).then(r=>r.json()).then(data => {
  const income = data.filter(r=>r.type==="income").reduce((s,r)=>s+r.amount,0);
  const expense = data.filter(r=>r.type==="expense").reduce((s,r)=>s+r.amount,0);
  document.getElementById("summary").innerHTML = [
    ["收入","#4CAF50",`¥${income.toFixed(2)}`],
    ["支出","#f44336",`¥${expense.toFixed(2)}`],
    ["结余","#667eea",`¥${(income-expense).toFixed(2)}`]
  ].map(([label,color,val])=>`<div style="flex:1;background:white;border-radius:12px;padding:12px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06)">
    <p style="font-size:12px;color:#999">${label}</p>
    <p style="font-size:18px;font-weight:600;color:${color};margin-top:4px">${val}</p>
  </div>`).join("");
  document.getElementById("records").innerHTML = data.slice().reverse().slice(0,30).map(r=>
    `<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #f5f5f5">
      <div><p style="font-size:14px">${r.category} ${r.note?`· ${r.note}`:""}</p><p style="font-size:12px;color:#999">${r.time.split("T")[0]}</p></div>
      <span style="font-size:15px;font-weight:600;color:${r.type==="income"?"#4CAF50":"#f44336"}">${r.type==="income"?"+":"-"}¥${r.amount}</span>
    </div>`).join("") || `<p style="color:#999;text-align:center;padding:20px">还没有记账，发送「花了xx元xxx」来记账</p>`;
});
</script>
""" + NAV_HTML

HABITS_HTML = BASE_CSS + """
<div class="header"><h1>🎯 习惯追踪</h1><p>坚持就是胜利</p></div>
<div class="card" id="habits-list"></div>
<script>
const uid = localStorage.getItem("uid") || "default";
const today = new Date().toISOString().split("T")[0];
fetch(`/api/habits?user_id=${uid}`).then(r=>r.json()).then(data => {
  document.getElementById("habits-list").innerHTML = data.length
    ? data.map(h => {
        const checked = (h.checkins||[]).includes(today);
        const streak = (h.checkins||[]).length;
        return `<div style="display:flex;align-items:center;padding:14px 0;border-bottom:1px solid #f5f5f5">
          <span style="font-size:28px;margin-right:12px">${checked?"✅":"⬜"}</span>
          <div style="flex:1"><p style="font-size:15px;font-weight:500">${h.name}</p><p style="font-size:12px;color:#999;margin-top:2px">累计打卡 ${streak} 天</p></div>
          <div style="text-align:center"><p style="font-size:20px;font-weight:700;color:#667eea">${streak}</p><p style="font-size:11px;color:#999">天</p></div>
        </div>`;
      }).join("")
    : `<p style="color:#999;text-align:center;padding:20px">还没有习惯，发送「添加习惯 xxx」来设定</p>`;
});
</script>
""" + NAV_HTML

MOOD_HTML = BASE_CSS + """
<div class="header"><h1>😊 情绪</h1><p>记录心情变化</p></div>
<div class="card" id="mood-chart"></div>
<div id="mood-list" style="padding:0 12px"></div>
<script>
const uid = localStorage.getItem("uid") || "default";
const emojis = ["","😢","😞","😟","😕","😐","🙂","😊","😄","😁","🤩"];
fetch(`/api/mood?user_id=${uid}`).then(r=>r.json()).then(data => {
  if(!data.length) { document.getElementById("mood-chart").innerHTML=`<p style="color:#999;text-align:center;padding:20px">暂无情绪数据</p>`; return; }
  // 简单条形图
  const bars = data.slice(0,7).reverse().map(m=>`
    <div style="display:flex;align-items:center;margin-bottom:8px">
      <span style="font-size:11px;color:#999;width:50px">${m.date.slice(5)}</span>
      <div style="flex:1;background:#f0f0f5;border-radius:4px;height:20px;margin:0 8px;overflow:hidden">
        <div style="width:${m.score*10}%;background:linear-gradient(135deg,#667eea,#764ba2);height:100%;border-radius:4px"></div>
      </div>
      <span>${emojis[m.score]||"😐"} ${m.score}</span>
    </div>`).join("");
  document.getElementById("mood-chart").innerHTML = `<h3 style="margin-bottom:12px;font-size:15px">近期情绪趋势</h3>${bars}`;
  document.getElementById("mood-list").innerHTML = data.map(m=>`<div class="card" style="margin-bottom:8px">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <span style="font-size:13px;color:#999">${m.date}</span>
      <span style="font-size:24px">${emojis[m.score]||"😐"}</span>
    </div>
    <p style="font-size:14px;margin-top:8px;line-height:1.5">${m.summary}</p>
  </div>`).join("");
});
</script>
""" + NAV_HTML
