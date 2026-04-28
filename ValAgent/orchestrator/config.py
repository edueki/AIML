from dotenv import load_dotenv
import os

load_dotenv()

MCP_HTTP_URL = os.getenv("MCP_HTTP_URL", "http://localhost:8000/mcp").rstrip("/")
INTENT_SERVER_URL = os.getenv("INTENT_SERVER_URL", "http://localhost:8087/intent")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
ORCH_TIMEOUT_SECONDS = float(os.getenv("ORCH_TIMEOUT_SECONDS", "15"))