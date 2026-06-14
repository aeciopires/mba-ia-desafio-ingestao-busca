import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
OPENAI_YAML_PATH = ROOT / "openai.yaml"
GEMINI_YAML_PATH = ROOT / "gemini.yaml"

DEFAULT_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/rag"
DEFAULT_PDF_PATH = ROOT / "document.pdf"
DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_OPENAI_LLM_MODEL = "gpt-5-nano"
DEFAULT_GOOGLE_EMBEDDING_MODEL = "models/embedding-001"
DEFAULT_GOOGLE_LLM_MODEL = "gemini-3.1-flash-lite-preview"
DEFAULT_DOCUMENT_TABLE = "documents"


def _load_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
            return data or {}
    except Exception:
        return {}


def _load_yaml_dict(env_key: str, default_path: Path) -> dict[str, Any]:
    path = os.getenv(env_key)
    if path:
        path = Path(path)
        if path.exists():
            return _load_yaml_file(path)
    return _load_yaml_file(default_path)


def get_openai_yaml() -> dict[str, Any]:
    return _load_yaml_dict("OPENAI_YAML", OPENAI_YAML_PATH)


def get_gemini_yaml() -> dict[str, Any]:
    return _load_yaml_dict("GEMINI_YAML", GEMINI_YAML_PATH)


def get_openai_api_key() -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key.strip()
    yaml_data = get_openai_yaml()
    return yaml_data.get("secret") or yaml_data.get("id")


def get_google_api_key() -> str | None:
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return api_key.strip()
    yaml_data = get_gemini_yaml()
    return yaml_data.get("secret") or yaml_data.get("id")


def get_openai_embedding_model() -> str:
    return os.getenv("OPENAI_EMBEDDING_MODEL", DEFAULT_OPENAI_EMBEDDING_MODEL).strip("'\" ")


def get_openai_llm_model() -> str:
    return os.getenv("OPENAI_LLM_MODEL", DEFAULT_OPENAI_LLM_MODEL).strip("'\" ")


def get_google_embedding_model() -> str:
    return os.getenv("GOOGLE_EMBEDDING_MODEL", DEFAULT_GOOGLE_EMBEDDING_MODEL).strip("'\" ")


def get_google_llm_model() -> str:
    return os.getenv("GOOGLE_LLM_MODEL", DEFAULT_GOOGLE_LLM_MODEL).strip("'\" ")


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_pdf_path() -> str:
    return os.getenv("PDF_PATH", str(DEFAULT_PDF_PATH))


def get_document_table_name() -> str:
    return os.getenv("PG_VECTOR_COLLECTION_NAME", DEFAULT_DOCUMENT_TABLE)


def get_llm_provider() -> str:
    return os.getenv("LLM_PROVIDER", "openai").strip().lower()
