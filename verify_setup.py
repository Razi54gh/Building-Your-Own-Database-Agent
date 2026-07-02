"""Cek apakah environment siap menjalankan notebook L2-L5."""

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent


def main() -> int:
    print("=" * 50)
    print("VERIFIKASI SETUP DATABASE AGENT")
    print("=" * 50)
    ok = True

    print(f"\n[1] Python: {sys.executable}")
    print(f"    Versi  : {sys.version.split()[0]}")

    packages = [
        "pandas",
        "langchain_openai",
        "langchain_experimental",
        "langchain_community",
        "openai",
        "sqlalchemy",
        "dotenv",
    ]
    print("\n[2] Package:")
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"    OK  {pkg}")
        except ImportError:
            print(f"    FAIL {pkg}  -> pip install -r requirements.txt")
            ok = False

    print("\n[3] File data:")
    for label, path in [
        ("CSV", BASE / "data" / "all-states-history.csv"),
        ("SQLite DB", BASE / "db" / "test.db"),
        (".env", BASE / ".env"),
    ]:
        status = "OK " if path.exists() else "FAIL"
        if not path.exists():
            ok = False
        print(f"    {status} {label}: {path}")

    print("\n[4] LLM Provider:")
    from llm_setup import check_llm_config, get_provider, get_model_name, print_provider_info

    print(f"    Provider = {get_provider()}")
    print(f"    Model    = {get_model_name()}")

    issues = check_llm_config()
    if issues:
        ok = False
        for issue in issues:
            print(f"    FAIL {issue}")
        provider = get_provider()
        if provider == "ollama":
            print("\n    Setup Ollama:")
            print("    1. Install: https://ollama.com")
            print("    2. ollama pull llama3.1:8b")
            print("    3. Pastikan Ollama app berjalan")
        elif provider == "groq":
            print("\n    Daftar API key: https://console.groq.com")
        elif provider == "openai":
            print("\n    API key: https://platform.openai.com/api-keys")
    else:
        print("    OK  Konfigurasi LLM valid")

    print("\n" + "=" * 50)
    if ok:
        print("SIAP! Jalankan notebook L2-L5 di VS Code.")
    else:
        print("BELUM SIAP. Perbaiki item FAIL di atas.")
    print("=" * 50)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
