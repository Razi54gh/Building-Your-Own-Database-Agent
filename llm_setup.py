"""Konfigurasi LLM multi-provider: Ollama, OpenAI, Groq, Azure."""

import os
import socket
import urllib.error
import urllib.request
from urllib.parse import urlparse

import config  # noqa: F401  # memuat .env

SUPPORTED_PROVIDERS = ("ollama", "openai", "groq", "azure")

AZURE_PLACEHOLDERS = (
    "nama-resource",
    "your-resource",
    "your-api-key",
    "sk-xxxxxxxx",
    "example.com",
)


def get_provider() -> str:
    return os.getenv("LLM_PROVIDER", "ollama").strip().lower()


def get_model_name() -> str:
    provider = get_provider()
    if provider == "ollama":
        return os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    if provider == "openai":
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if provider == "groq":
        return os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    return os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4-1106")


def _api_key() -> str | None:
    return os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_KEY")


def _normalize_endpoint(raw: str | None) -> str | None:
    if not raw:
        return None
    endpoint = raw.strip().rstrip("/")
    if not endpoint.startswith(("http://", "https://")):
        endpoint = f"https://{endpoint}"
    return endpoint


def _is_azure_placeholder(value: str | None) -> bool:
    if not value:
        return True
    lowered = value.lower()
    return any(marker in lowered for marker in AZURE_PLACEHOLDERS)


def _ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")


def _can_resolve(host: str) -> bool:
    try:
        socket.getaddrinfo(host, 443)
        return True
    except socket.gaierror:
        return False


def _ollama_is_running() -> bool:
    url = f"{_ollama_base_url()}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def check_llm_config() -> list[str]:
    """Kembalikan daftar masalah konfigurasi (kosong = siap)."""
    provider = get_provider()
    issues: list[str] = []

    if provider not in SUPPORTED_PROVIDERS:
        issues.append(
            f"LLM_PROVIDER='{provider}' tidak dikenal. "
            f"Pilih: {', '.join(SUPPORTED_PROVIDERS)}"
        )
        return issues

    if provider == "ollama":
        if not _ollama_is_running():
            issues.append(
                "Ollama tidak berjalan. Install dari https://ollama.com lalu jalankan: "
                "ollama serve  (atau buka aplikasi Ollama)"
            )
        model = get_model_name()
        if not model:
            issues.append("OLLAMA_MODEL belum diisi di .env")

    elif provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key or key.startswith("sk-xxx"):
            issues.append(
                "OPENAI_API_KEY belum diisi. Dapatkan di https://platform.openai.com/api-keys"
            )

    elif provider == "groq":
        key = os.getenv("GROQ_API_KEY")
        if not key or "xxx" in key.lower():
            issues.append(
                "GROQ_API_KEY belum diisi. Daftar gratis di https://console.groq.com"
            )

    elif provider == "azure":
        endpoint = _normalize_endpoint(os.getenv("AZURE_OPENAI_ENDPOINT"))
        api_key = _api_key()
        if not endpoint:
            issues.append("AZURE_OPENAI_ENDPOINT belum diisi di file .env")
        elif _is_azure_placeholder(endpoint):
            issues.append("AZURE_OPENAI_ENDPOINT masih placeholder.")
        elif not endpoint.endswith(".openai.azure.com"):
            issues.append("AZURE_OPENAI_ENDPOINT format: https://NAMA.openai.azure.com")
        if not api_key:
            issues.append("AZURE_OPENAI_API_KEY belum diisi di file .env")
        elif _is_azure_placeholder(api_key):
            issues.append("AZURE_OPENAI_API_KEY masih placeholder.")
        if endpoint and not _is_azure_placeholder(endpoint):
            host = urlparse(endpoint).hostname
            if host and not _can_resolve(host):
                issues.append(f"Tidak bisa resolve hostname Azure: {host}")

    return issues


# Alias lama (notebook sebelumnya)
check_azure_config = check_llm_config


def get_agent_type() -> str:
    """Ollama: pakai jalur sederhana (sql_helper), bukan agent penuh."""
    provider = get_provider()
    if provider == "ollama":
        return "zero-shot-react-description"
    return os.getenv("AGENT_TYPE", "tool-calling")


def use_simple_sql() -> bool:
    """Ollama lokal lebih stabil dengan ask_sql_simple()."""
    return get_provider() == "ollama"


def get_agent_executor_kwargs() -> dict:
    """Opsi AgentExecutor. Jangan sertakan max_iterations (sudah ada di create_*_agent)."""
    return {
        "handle_parsing_errors": True,
    }


def get_chat_model(**kwargs):
    """Buat model LangChain sesuai provider."""
    provider = get_provider()

    if provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError as exc:
            raise ImportError(
                "Install dulu: pip install langchain-ollama"
            ) from exc

        defaults = {
            "base_url": _ollama_base_url(),
            "model": get_model_name(),
            "temperature": 0,
            "num_ctx": 4096,
            "num_predict": 512,
            "keep_alive": "5m",
        }
        defaults.update(kwargs)
        return ChatOllama(**defaults)

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        defaults = {
            "model": get_model_name(),
            "api_key": os.getenv("OPENAI_API_KEY"),
            "temperature": 0,
        }
        defaults.update(kwargs)
        return ChatOpenAI(**defaults)

    if provider == "groq":
        try:
            from langchain_groq import ChatGroq
        except ImportError as exc:
            raise ImportError(
                "Install dulu: pip install langchain-groq"
            ) from exc

        defaults = {
            "model": get_model_name(),
            "api_key": os.getenv("GROQ_API_KEY"),
            "temperature": 0,
        }
        defaults.update(kwargs)
        return ChatGroq(**defaults)

    from langchain_openai import AzureChatOpenAI

    endpoint = _normalize_endpoint(os.getenv("AZURE_OPENAI_ENDPOINT"))
    defaults = {
        "openai_api_version": "2023-05-15",
        "azure_deployment": get_model_name(),
        "azure_endpoint": endpoint,
        "api_key": _api_key(),
        "temperature": 0,
    }
    defaults.update(kwargs)
    return AzureChatOpenAI(**defaults)


def get_openai_client(api_version: str = "2023-05-15"):
    """Klien OpenAI-compatible untuk function calling (L4/L5)."""
    from openai import AzureOpenAI, OpenAI

    provider = get_provider()

    if provider == "ollama":
        return OpenAI(
            base_url=f"{_ollama_base_url()}/v1",
            api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
        )

    if provider == "openai":
        return OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    if provider == "groq":
        return OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
        )

    endpoint = _normalize_endpoint(os.getenv("AZURE_OPENAI_ENDPOINT"))
    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=_api_key(),
        api_version=api_version,
    )


def get_deployment_name() -> str:
    return get_model_name()


def supports_assistants_api() -> bool:
    """Assistants API resmi hanya Azure/OpenAI."""
    return get_provider() in ("azure", "openai")


def print_provider_info() -> None:
    provider = get_provider()
    print(f"Provider : {provider}")
    print(f"Model    : {get_model_name()}")
    if provider == "ollama":
        print(f"Ollama   : {_ollama_base_url()}")
