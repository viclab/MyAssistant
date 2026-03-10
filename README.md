# MyAssistant - 企业微信 AI 生活助手

基于 Ollama 本地模型的企业微信 AI 助手，支持速记、待办、日记、情绪、财务、习惯追踪等功能，图文并茂展示。

## 功能

- 📝 **速记**：聊天消息（文字+图片）自动保存，瀑布流图文展示
- ✅ **待办**：自然语言管理任务，支持截止日期
- 📔 **日记**：AI 自动整理当天消息生成日记
- 😊 **情绪**：每日情绪分析，可视化趋势
- 💰 **财务**：自然语言记账，收支统计
- 🎯 **习惯**：设定习惯目标，打卡追踪
- 📊 **周报/月报**：AI 自动生成总结报告

## 部署步骤

### 1. 确保 Ollama 已运行

```bash
ollama pull qwen2.5:3b
ollama serve
```

验证：
```bash
curl http://localhost:11434/api/tags
```

### 2. 克隆并配置

```bash
git clone <your-repo>
cd MyAssistant
cp .env.example src/.env
nano src/.env   # 填入企微配置
```

### 3. 填写 .env 配置

| 变量 | 说明 | 获取方式 |
|---|---|---|
| WEWORK_CORP_ID | 企业ID | 企微管理后台→我的企业 |
| WEWORK_AGENT_ID | 应用AgentID | 企微管理后台→应用管理→你的应用 |
| WEWORK_CORP_SECRET | 应用Secret | 同上 |
| WEWORK_TOKEN | 回调Token | 自己设定一串随机字符串 |
| WEWORK_ENCODING_AES_KEY | 回调加密Key | 自己设定43位随机字符串 |
| DEFAULT_USER_ID | 你的企微账号 | 企微个人信息中的账号 |
| ADMIN_TOKEN | Web后台密码 | 自己设定 |
| WEB_DOMAIN | 服务器IP:端口 | 如 43.134.142.4:9000 |

### 4. 启动服务

```bash
cd deploy
docker-compose up -d --build
```

查看日志：
```bash
docker-compose logs -f
```

### 5. 配置企微回调

在企业微信管理后台 → 应用管理 → 你的应用 → 接收消息：

- URL: `http://你的服务器IP:9000/wework`
- Token: 与 .env 中的 WEWORK_TOKEN 一致
- EncodingAESKey: 与 .env 中的 WEWORK_ENCODING_AES_KEY 一致

### 6. 访问 Web 端

```
http://你的服务器IP:9000/web/login
```

## 使用示例

| 发送内容 | 效果 |
|---|---|
| `今天买菜花了30元` | 记账支出30元 |
| `明天下午3点开会` | 添加待办 |
| `完成1` | 完成第1条待办 |
| `查看待办` | 列出所有未完成待办 |
| `添加习惯 每天读书30分钟` | 创建习惯 |
| `打卡` | 今日习惯打卡 |
| `生成今日日记` | AI 整理今日记录 |
| `本周收入5000` | 记录收入 |

## 项目结构

```
MyAssistant/
├── src/
│   ├── app.py              # Flask 主入口
│   ├── brain.py            # AI 处理核心（Ollama）
│   ├── config.py           # 配置
│   ├── storage.py          # 数据存储
│   ├── wework_crypto.py    # 企微消息加解密
│   ├── scheduler.py        # 定时任务
│   ├── web_routes.py       # Web 页面和 API
│   └── requirements.txt
├── data/                   # 数据目录（自动创建）
├── deploy/
│   ├── docker-compose.yml
│   └── Dockerfile
└── .env.example
```
