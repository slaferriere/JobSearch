import time

import httpx

from app.connectors.base import Connector, NormalizedJob, guess_remote_type


class UsaJobsConnector(Connector):
    source_key = "usajobs"

    def __init__(self, api_key: str, user_agent_email: str, keywords: list[str]):
        self.api_key = api_key
        self.user_agent_email = user_agent_email
        self.keywords = keywords or [""]

    def fetch_normalized(self) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        headers = {
            "Authorization-Key": self.api_key,
            "User-Agent": self.user_agent_email,
            "Host": "data.usajobs.gov",
        }
        with httpx.Client(headers=headers, timeout=30.0) as client:
            for keyword in self.keywords:
                page = 1
                while True:
                    params = {"ResultsPerPage": 500, "Page": page}
                    if keyword:
                        params["Keyword"] = keyword
                    try:
                        resp = client.get("https://data.usajobs.gov/api/search", params=params)
                        resp.raise_for_status()
                    except httpx.HTTPError:
                        break
                    data = resp.json()
                    items = data.get("SearchResult", {}).get("SearchResultItems", [])
                    if not items:
                        break
                    for item in items:
                        job = self._normalize(item.get("MatchedObjectDescriptor", {}))
                        if job:
                            jobs.append(job)
                    total_pages = int(
                        data.get("SearchResult", {})
                        .get("SearchResultCountAll", 0)
                    )
                    if len(items) < 500 or page * 500 >= total_pages:
                        break
                    page += 1
                    time.sleep(2)
        return jobs

    def _normalize(self, d: dict) -> NormalizedJob | None:
        if not d:
            return None
        title = d.get("PositionTitle", "")
        org = d.get("OrganizationName", "")
        locations = d.get("PositionLocation") or []
        location_raw = "; ".join(
            loc.get("LocationName", "") for loc in locations if loc.get("LocationName")
        ) or None

        remuneration = (d.get("PositionRemuneration") or [{}])[0]
        salary_min = _to_int(remuneration.get("MinimumRange"))
        salary_max = _to_int(remuneration.get("MaximumRange"))

        summary = (d.get("UserArea", {}).get("Details", {}) or {}).get("JobSummary", "")
        apply_uris = d.get("ApplyURI") or []
        apply_url = apply_uris[0] if apply_uris else d.get("PositionURI", "")

        return NormalizedJob(
            source=self.source_key,
            source_id=d.get("PositionID", d.get("PositionURI", title)),
            title=title,
            company=org,
            location_raw=location_raw,
            remote_type=guess_remote_type(title, location_raw, summary[:500]),
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency="USD",
            description_html=None,
            description_text=summary,
            apply_url=apply_url,
            apply_url_is_redirect=False,
            posted_date=d.get("PublicationStartDate"),
            raw=d,
        )


def _to_int(value) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None
