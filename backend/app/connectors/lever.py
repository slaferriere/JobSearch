import time

import httpx

from app.connectors.base import Connector, NormalizedJob, guess_remote_type
from app.connectors.greenhouse import USER_AGENT, strip_html

WORKPLACE_TYPE_MAP = {"remote": "remote", "hybrid": "hybrid", "on-site": "onsite", "onsite": "onsite"}


class LeverConnector(Connector):
    source_key = "lever"

    def __init__(self, companies: dict[str, str]):
        """companies: {lever_company_slug: display_name}"""
        self.companies = companies

    def fetch_normalized(self) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=30.0) as client:
            for slug, display_name in self.companies.items():
                url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
                try:
                    resp = client.get(url)
                    if resp.status_code == 404:
                        continue
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue
                for raw in resp.json():
                    jobs.append(self._normalize(raw, display_name))
                time.sleep(1)
        return jobs

    def _normalize(self, raw: dict, company_name: str) -> NormalizedJob:
        categories = raw.get("categories") or {}
        location = categories.get("location")
        description_html = raw.get("description")
        description_text = raw.get("descriptionPlain") or strip_html(description_html)

        workplace_type = raw.get("workplaceType")
        remote_type = WORKPLACE_TYPE_MAP.get(
            (workplace_type or "").lower(),
            guess_remote_type(raw.get("text"), location, description_text[:500]),
        )

        created_at_ms = raw.get("createdAt")
        posted_date = None
        if created_at_ms:
            from datetime import datetime, timezone

            posted_date = datetime.fromtimestamp(created_at_ms / 1000, tz=timezone.utc).isoformat()

        return NormalizedJob(
            source=self.source_key,
            source_id=str(raw["id"]),
            title=raw.get("text", ""),
            company=company_name,
            location_raw=location,
            remote_type=remote_type,
            salary_min=None,
            salary_max=None,
            salary_currency="USD",
            description_html=description_html,
            description_text=description_text,
            apply_url=raw.get("applyUrl") or raw.get("hostedUrl", ""),
            apply_url_is_redirect=False,
            posted_date=posted_date,
            raw=raw,
        )
