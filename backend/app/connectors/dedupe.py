import hashlib
import re


def content_hash(company: str, title: str, location: str | None) -> str:
    def normalize(s: str | None) -> str:
        return re.sub(r"\s+", " ", (s or "").strip().lower())

    key = f"{normalize(company)}|{normalize(title)}|{normalize(location)}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()
