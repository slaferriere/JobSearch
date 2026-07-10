import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import httpx

from app.connectors.base import Connector, NormalizedJob, guess_remote_type
from app.connectors.greenhouse import USER_AGENT, strip_html

PAGE_SIZE = 20
MAX_RESULTS_PER_COMPANY = 60
MAX_PAGES_PER_QUERY = 10
REQUEST_SLEEP_SECONDS = 0.3


@dataclass
class WorkdayCompany:
    tenant: str
    wd_host: str  # e.g. "wd5" in {tenant}.wd5.myworkdayjobs.com
    site: str  # e.g. "NVIDIAExternalCareerSite"
    display_name: str

    @property
    def base_url(self) -> str:
        return f"https://{self.tenant}.{self.wd_host}.myworkdayjobs.com/wday/cxs/{self.tenant}/{self.site}"


def _posted_on_to_date(posted_on: str | None) -> str | None:
    """Workday only gives relative text like 'Posted Today' / 'Posted 3 Days Ago'."""
    if not posted_on:
        return None
    now = datetime.now(timezone.utc)
    lowered = posted_on.lower()
    if "today" in lowered:
        return now.date().isoformat()
    if "yesterday" in lowered:
        return (now - timedelta(days=1)).date().isoformat()
    digits = "".join(c for c in lowered.split(" days")[0] if c.isdigit())
    if digits.isdigit():
        return (now - timedelta(days=int(digits))).date().isoformat()
    return None


class WorkdayConnector(Connector):
    source_key = "workday"

    def __init__(self, companies: list[WorkdayCompany], search_keywords: list[str]):
        self.companies = companies
        self.search_keywords = search_keywords or [""]

    def fetch_normalized(self) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        with httpx.Client(headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"}, timeout=30.0) as client:
            for company in self.companies:
                for raw in self._fetch_company(client, company):
                    jobs.append(self._normalize(raw, company))
        return jobs

    def _fetch_company(self, client: httpx.Client, company: WorkdayCompany) -> list[dict]:
        seen_paths: dict[str, dict] = {}
        for keyword in self.search_keywords:
            if len(seen_paths) >= MAX_RESULTS_PER_COMPANY:
                break
            offset = 0
            for _ in range(MAX_PAGES_PER_QUERY):
                if len(seen_paths) >= MAX_RESULTS_PER_COMPANY:
                    break
                body = {"appliedFacets": {}, "limit": PAGE_SIZE, "offset": offset, "searchText": keyword}
                try:
                    resp = client.post(f"{company.base_url}/jobs", json=body)
                    resp.raise_for_status()
                except httpx.HTTPError:
                    break
                time.sleep(REQUEST_SLEEP_SECONDS)
                data = resp.json()
                postings = data.get("jobPostings") or []
                if not postings:
                    break
                for posting in postings:
                    path = posting.get("externalPath")
                    if path and path not in seen_paths:
                        seen_paths[path] = posting
                offset += PAGE_SIZE
                if offset >= data.get("total", 0):
                    break

        detailed: list[dict] = []
        for path, posting in list(seen_paths.items())[:MAX_RESULTS_PER_COMPANY]:
            try:
                resp = client.get(f"{company.base_url}{path}")
                resp.raise_for_status()
            except httpx.HTTPError:
                continue
            time.sleep(REQUEST_SLEEP_SECONDS)
            info = resp.json().get("jobPostingInfo")
            if info:
                detailed.append(info)
        return detailed

    def _normalize(self, info: dict, company: WorkdayCompany) -> NormalizedJob:
        description_html = info.get("jobDescription")
        description_text = strip_html(description_html)
        location = info.get("location")
        req_id = info.get("jobReqId") or info.get("jobPostingId", "")

        return NormalizedJob(
            source=self.source_key,
            source_id=f"{company.tenant}:{req_id}",
            title=info.get("title", ""),
            company=company.display_name,
            location_raw=location,
            remote_type=guess_remote_type(info.get("title"), location, description_text[:500]),
            salary_min=None,
            salary_max=None,
            salary_currency="USD",
            description_html=description_html,
            description_text=description_text,
            apply_url=info.get("externalUrl", ""),
            apply_url_is_redirect=False,
            posted_date=_posted_on_to_date(info.get("postedOn")) or info.get("startDate"),
            raw=info,
        )
