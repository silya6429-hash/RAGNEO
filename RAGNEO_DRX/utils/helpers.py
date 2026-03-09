import json
import hashlib
from pathlib import Path
from typing import List, Generator, Any


def ensure_dir(path: Path):
    """
    Создать директорию если не существует
    """
    path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path):

    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path: Path):

    ensure_dir(path.parent)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def hash_text(text: str) -> str:
    """
    Создание MD5 хеша текста
    """
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def batch_iterator(data: List[Any], batch_size: int) -> Generator:

    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]


def normalize_text(text: str) -> str:

    text = text.replace("\n", " ")
    text = text.replace("\t", " ")

    return " ".join(text.split())