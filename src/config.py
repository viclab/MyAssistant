import os
from dotenv import load_dotenv

load_dotenv()

# 企业微信
WEWORK_CORP_ID = os.getenv("WEWORK_CORP_ID", "")
WEWORK_AGENT_ID = os.getenv("WEWORK_AGENT_ID", "")
WEWORK_CORP_SECRET = os.getenv("WEWORK_CORP_SECRET", "")
WEWORK_TOKEN = os.getenv("WEWORK_TOKEN", "")
WEWORK_ENCODING_AES_KEY = os.getenv("WEWORK_ENCODING_AES_KEY", "")
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "")

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

# Web
WEB_DOMAIN = os.getenv("WEB_DOMAIN", "127.0.0.1:9000")
SERVER_PORT = int(os.getenv("SERVER_PORT", "9000"))
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin123")

# 数据目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
