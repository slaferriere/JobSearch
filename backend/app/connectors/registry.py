"""Default seed sources. Board tokens/slugs verified to resolve as of project setup.

Edit these dicts (or expose an editing UI later) to add/remove companies. Greenhouse
tokens come from a company's public jobs page URL: boards.greenhouse.io/{token}.
Lever slugs come from jobs.lever.co/{slug}.
"""

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
}

LEVER_COMPANIES: dict[str, str] = {
    "palantir": "Palantir",
    "spotify": "Spotify",
    "kraken": "Kraken",
    "tala": "Tala",
    "clari": "Clari",
    "findhelp": "findhelp",
}

# Empty string keyword pulls the general search feed; add specific keywords
# (e.g. "software engineer", "data analyst") to narrow results.
USAJOBS_KEYWORDS: list[str] = [""]
