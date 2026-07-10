"""Default seed sources. Board tokens/slugs verified to resolve as of project setup.

Edit these dicts (or expose an editing UI later) to add/remove companies. Greenhouse
tokens come from a company's public jobs page URL: boards.greenhouse.io/{token}.
Lever slugs come from jobs.lever.co/{slug}. Workday tenant/host/site come from a
company's myworkdayjobs.com URL (https://{tenant}.{host}.myworkdayjobs.com/{site})
and are NOT guessable from the company name alone -- verify a new entry by curling
https://{tenant}.{host}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs (POST,
body {"appliedFacets":{},"limit":5,"offset":0,"searchText":""}) before adding it.

Many large enterprises (Lockheed Martin, L3Harris, BAE Systems, Goldman Sachs,
Charles Schwab, JPMorgan, Google, Microsoft, Amazon, Apple, Meta, Oracle, IBM, ...)
run on a proprietary/custom careers platform with no public API and are
intentionally excluded here, same rationale as the LinkedIn/ClearanceJobs exclusion.
"""

from app.connectors.workday import WorkdayCompany

GREENHOUSE_COMPANIES: dict[str, str] = {
    "stripe": "Stripe",
    "airbnb": "Airbnb",
    "robinhood": "Robinhood",
    "coinbase": "Coinbase",
    "pinterest": "Pinterest",
    "databricks": "Databricks",
    "figma": "Figma",
    "instacart": "Instacart",
    "affirm": "Affirm",
    "asana": "Asana",
    "cloudflare": "Cloudflare",
    "reddit": "Reddit",
    "squarespace": "Squarespace",
    "discord": "Discord",
    "brex": "Brex",
    "gitlab": "GitLab",
    "dropbox": "Dropbox",
    "andurilindustries": "Anduril",
}

LEVER_COMPANIES: dict[str, str] = {
    "palantir": "Palantir",
    "spotify": "Spotify",
    "kraken": "Kraken",
    "tala": "Tala",
    "clari": "Clari",
    "findhelp": "findhelp",
}

WORKDAY_COMPANIES: list[WorkdayCompany] = [
    # Defense
    WorkdayCompany("globalhr", "wd5", "REC_RTX_Ext_Gateway", "RTX (Raytheon)"),
    WorkdayCompany("ngc", "wd1", "Northrop_Grumman_External_Site", "Northrop Grumman"),
    WorkdayCompany("boeing", "wd1", "EXTERNAL_CAREERS", "Boeing"),
    WorkdayCompany("leidos", "wd5", "External", "Leidos"),
    WorkdayCompany("bah", "wd1", "BAH_Jobs", "Booz Allen Hamilton"),
    WorkdayCompany("gdit", "wd5", "External_Career_Site", "General Dynamics IT"),
    # Financial
    WorkdayCompany("ms", "wd5", "External", "Morgan Stanley"),
    WorkdayCompany("ghr", "wd1", "Lateral-US", "Bank of America"),
    WorkdayCompany("wf", "wd1", "WellsFargoJobs", "Wells Fargo"),
    WorkdayCompany("citi", "wd5", "2", "Citigroup"),
    WorkdayCompany("capitalone", "wd12", "Capital_One", "Capital One"),
    WorkdayCompany("blackrock", "wd1", "BlackRock_Professional", "BlackRock"),
    # Tech
    WorkdayCompany("nvidia", "wd5", "NVIDIAExternalCareerSite", "NVIDIA"),
    WorkdayCompany("salesforce", "wd12", "External_Career_Site", "Salesforce"),
]

# Each keyword is a separate Workday search query per company (results are deduped),
# so this list covers both a software/RPA-developer resume and an architect-track
# resume without needing per-resume connector config. Add/remove terms as your
# target roles change.
WORKDAY_SEARCH_KEYWORDS: list[str] = [
    "software engineer",
    "rpa",
    "automation",
    "solutions architect",
    "systems architect",
    "cloud architect",
]

# Empty string keyword pulls the general search feed; add specific keywords
# (e.g. "software engineer", "data analyst") to narrow results.
USAJOBS_KEYWORDS: list[str] = [""]
