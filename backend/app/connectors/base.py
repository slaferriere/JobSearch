from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class NormalizedJob:
    source: str
    source_id: str
    title: str
    company: str
    location_raw: str | None
    remote_type: str  # remote | hybrid | onsite | unknown
    salary_min: int | None
    salary_max: int | None
    salary_currency: str
    description_html: str | None
    description_text: str | None
    apply_url: str
    apply_url_is_redirect: bool
    posted_date: str | None
    raw: dict = field(default_factory=dict)


class Connector(ABC):
    source_key: str

    @abstractmethod
    def fetch_normalized(self) -> list[NormalizedJob]:
        """Fetch and normalize all current listings from this source."""
        raise NotImplementedError


REMOTE_KEYWORDS = ("remote",)
HYBRID_KEYWORDS = ("hybrid",)


def guess_remote_type(*texts: str | None) -> str:
    joined = " ".join(t for t in texts if t).lower()
    if any(k in joined for k in HYBRID_KEYWORDS):
        return "hybrid"
    if any(k in joined for k in REMOTE_KEYWORDS):
        return "remote"
    if joined.strip():
        return "onsite"
    return "unknown"
