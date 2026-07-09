import re
import time

import httpx

from app.connectors.base import Connector, NormalizedJob, guess_remote_type

USER_AGENT = "PickEmStats-JobSearch/1.0 (personal project; contact via GitHub)"


def strip_html(html: str | None) -> str:
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


class GreenhouseConnector(Connector):
    source_key = "greenhouse"

    def __init__(self, companies: dict[str, str]):
        """companies: {board_token: display_name}"""
        self.companies = companies

    def fetch_normalized(self) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=30.0) as client:
            for token, display_name in self.companies.items():
                url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
                try:
                    resp = client.get(url)
                    if resp.status_code == 404:
                        continue
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue
                for raw in resp.json().get("jobs", []):
                    jobs.append(self._normalize(raw, display_name))
                time.sleep(1)
        return jobs

    def _normalize(self, raw: dict, company_name: str) -> NormalizedJob:
        location = (raw.get("location") or {}).get("name")
        description_html = raw.get("content")
        description_text = strip_html(description_html)
        return NormalizedJob(
            source=self.source_key,
            source_id=str(raw["id"]),
            title=raw.get("title", ""),
            company=company_name,
            location_raw=location,
            remote_type=guess_remote_type(raw.get("title"), location, description_text[:500]),
            salary_min=None,
            salary_max=None,
            salary_currency="USD",
            description_html=description_html,
            description_text=description_text,
            apply_url=raw.get("absolute_url", ""),
            apply_url_is_redirect=False,
            posted_date=raw.get("updated_at"),
            raw=raw,
        )
