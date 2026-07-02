"""Load Azure OpenAI credentials from .env for local VS Code / Jupyter runs."""

from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

ENV_PATH = Path(__file__).resolve().parent / ".env"

if load_dotenv and ENV_PATH.exists():
    load_dotenv(ENV_PATH)
