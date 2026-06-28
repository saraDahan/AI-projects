# config.py — Centralised application configuration.
#
# All tuneable constants live here so that app.py and chat_service.py
# never contain magic strings or numbers.

# ---------------------------------------------------------------------------
# UI text
# ---------------------------------------------------------------------------

APP_TITLE: str = "🤖 AI Chatbot"
APP_DESCRIPTION: str = (
    "A modern AI-powered chatbot. "
    "Type a message below and press **Enter** or click **Send**."
)

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

# CHATBOT_HEIGHT is now controlled via CSS (vh units) — see _CSS in app.py
MAX_CONTENT_WIDTH: int = 1300     # pixels — centres the chat on wide screens

# ---------------------------------------------------------------------------
# Input field
# ---------------------------------------------------------------------------

TEXTBOX_PLACEHOLDER: str = "Type your message here…"
TEXTBOX_LABEL: str = "Your message"

# ---------------------------------------------------------------------------
# Backend provider selector
#
# Swap this value (or read it from an environment variable) to change the
# active AI backend without touching any other file.
#
# Supported values (to be implemented in chat_service.py):
#   "mock"       – echo-style placeholder (default)
#   "openai"     – OpenAI Chat Completions API
#   "gemini"     – Google Gemini API
#   "claude"     – Anthropic Claude API
#   "langchain"  – LangChain pipeline
#   "llamaindex" – LlamaIndex RAG pipeline
# ---------------------------------------------------------------------------

ACTIVE_PROVIDER: str = "llamaindex"

# The LLM model used for response generation (Cohere).
# command-r-plus was retired on September 15, 2025.
# command-a-03-2025 is the current replacement.
COHERE_LLM_MODEL: str = "command-a-03-2025"
