#!/usr/bin/env python3
"""
Validar requisitos do projeto.
"""
import os
import sys
import shutil
from pathlib import Path
from typing import Tuple

# Cores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

ROOT = Path(__file__).resolve().parent.parent


def success(msg: str) -> None:
    print(f"{GREEN}✓ {msg}{RESET}")


def error(msg: str) -> None:
    print(f"{RED}✗ {msg}{RESET}")


def warning(msg: str) -> None:
    print(f"{YELLOW}⚠ {msg}{RESET}")


def check_python() -> bool:
    """Verifica se Python 3.10+ está instalado."""
    major, minor = sys.version_info.major, sys.version_info.minor
    if major >= 3 and minor >= 10:
        success(f"Python {major}.{minor}.{sys.version_info.micro} ✓")
        return True
    error(f"Python 3.10+ required, found {major}.{minor}")
    return False


def check_docker() -> bool:
    """Verifica se docker e docker-compose estão instalados."""
    if not shutil.which("docker"):
        error("docker não encontrado. Instale: https://docs.docker.com/get-docker/")
        return False
    success("docker instalado ✓")

    if not shutil.which("docker-compose"):
        error("docker-compose não encontrado. Instale: https://docs.docker.com/compose/install/")
        return False
    success("docker-compose instalado ✓")
    return True


def check_pdf() -> bool:
    """Verifica se o PDF existe."""
    pdf_path = ROOT / "document.pdf"
    if not pdf_path.exists():
        error(f"PDF não encontrado em: {pdf_path}")
        return False
    success(f"PDF encontrado: {pdf_path}")
    return True


def check_api_keys() -> Tuple[bool, str]:
    """Verifica se as chaves de API estão configuradas."""
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    openai_yaml = ROOT / "openai.yaml"
    gemini_yaml = ROOT / "gemini.yaml"

    has_openai = bool(openai_key) or (openai_yaml.exists() and "secret:" in openai_yaml.read_text())
    has_google = bool(google_key) or (gemini_yaml.exists() and "secret:" in gemini_yaml.read_text())

    if has_openai:
        success("OpenAI API key configurada ✓")
    else:
        warning("OpenAI API key não configurada. Configure openai.yaml ou OPENAI_API_KEY")

    if has_google:
        success("Google API key configurada ✓")
    else:
        warning("Google API key não configurada. Configure gemini.yaml ou GOOGLE_API_KEY")

    if has_openai or has_google:
        return True, "openai" if has_openai else "google"
    
    error("Nenhuma chave de API configurada. Configure openai.yaml/gemini.yaml ou variáveis de ambiente.")
    return False, ""


def check_dependencies() -> bool:
    """Verifica se as dependências Python estão instaladas."""
    required = {
        "langchain": "langchain",
        "langchain_openai": "langchain_openai",
        "langchain_community": "langchain_community",
        "langchain_text_splitters": "langchain_text_splitters",
        "langchain_google_genai": "langchain_google_genai",
        "pypdf": "pypdf",
        "psycopg2": "psycopg2",
        "pgvector": "pgvector",
        "python-dotenv": "dotenv",
    }
    
    missing = []
    for pkg, import_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        error(f"Pacotes faltando: {', '.join(missing)}")
        error("Execute: pip install -r requirements.txt")
        return False
    
    success("Todas as dependências instaladas ✓")
    return True


def check_database_connection() -> bool:
    """Verifica se o banco de dados está acessível."""
    try:
        sys.path.insert(0, str(ROOT))
        from src.config import get_database_url
        import psycopg2
        db_url = get_database_url()
        # Parse connection string
        if "postgresql://" in db_url or "postgresql+psycopg2://" in db_url:
            success(f"DATABASE_URL configurada: {db_url[:50]}... ✓")
            return True
    except Exception as e:
        error(f"Erro ao validar DATABASE_URL: {e}")
        return False


def validate_all() -> bool:
    """Executa todas as validações."""
    print("\n" + "=" * 60)
    print("VALIDAÇÃO DE REQUISITOS")
    print("=" * 60 + "\n")

    checks = [
        ("Python", check_python),
        ("Docker", check_docker),
        ("PDF", check_pdf),
        ("Dependências", check_dependencies),
        ("Database", check_database_connection),
    ]

    results = []
    for name, check_fn in checks:
        print(f"\n📋 Verificando {name}...")
        try:
            result = check_fn()
            results.append(result)
        except Exception as e:
            error(f"Erro ao verificar {name}: {e}")
            results.append(False)

    api_ok, provider = check_api_keys()
    results.append(api_ok)

    print("\n" + "=" * 60)
    if all(results):
        success("✓ TODOS OS REQUISITOS VALIDADOS")
        print("=" * 60 + "\n")
        return True
    else:
        error("✗ ALGUNS REQUISITOS FALTAM")
        print("=" * 60 + "\n")
        return False


if __name__ == "__main__":
    ok = validate_all()
    sys.exit(0 if ok else 1)
