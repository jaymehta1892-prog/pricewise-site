#!/usr/bin/env python3
"""
Update stats.json with the total number of App Store first-time downloads for
Pricewise Grocery, using the App Store Connect Sales & Trends API.

SECURITY: all credentials are read from environment variables. Set these as
GitHub repository *Secrets* (Settings -> Secrets and variables -> Actions).
NEVER commit your .p8 private key or any of these values to the repository.

Required env vars:
  ASC_ISSUER_ID       Issuer ID (App Store Connect -> Users and Access -> Integrations)
  ASC_KEY_ID          Key ID of your App Store Connect API key
  ASC_PRIVATE_KEY     Full contents of the .p8 file (the -----BEGIN PRIVATE KEY----- block)
  ASC_VENDOR_NUMBER   Your vendor number (App Store Connect -> Payments and Financial Reports)

Optional env vars:
  APP_APPLE_ID        default "6770648419"
  APP_RELEASE_DATE    default "2026-06-04" (first date to back-fill from)
  STATS_PATH          default "stats.json"
"""
import os, sys, json, time, gzip, datetime as dt
import jwt          # pip install "pyjwt[crypto]"
import requests

API = "https://api.appstoreconnect.apple.com/v1/salesReports"

# Product Type Identifiers that represent a *first-time download* (an install),
# as opposed to updates ("7"-family) or re-downloads ("3"-family).
FIRST_DOWNLOAD_PTI = {"1", "1E", "1EP", "1EU", "1F", "1T", "F1", "FF1"}


def make_token(issuer_id, key_id, private_key):
    now = int(time.time())
    payload = {"iss": issuer_id, "iat": now, "exp": now + 15 * 60, "aud": "appstoreconnect-v1"}
    return jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": key_id, "typ": "JWT"})


def parse_downloads(tsv_text, apple_id):
    """Sum first-time-download Units for the given Apple Identifier from a Sales report TSV."""
    lines = tsv_text.splitlines()
    if not lines:
        return 0
    header = lines[0].split("\t")
    idx = {h.strip(): i for i, h in enumerate(header)}
    pti_i = idx.get("Product Type Identifier")
    units_i = idx.get("Units")
    appid_i = idx.get("Apple Identifier")
    if pti_i is None or units_i is None:
        return 0
    total = 0
    for line in lines[1:]:
        if not line.strip():
            continue
        c = line.split("\t")
        if len(c) <= max(pti_i, units_i):
            continue
        if appid_i is not None and len(c) > appid_i and c[appid_i].strip() != str(apple_id):
            continue
        if c[pti_i].strip() in FIRST_DOWNLOAD_PTI:
            try:
                total += int(c[units_i].strip())
            except ValueError:
                pass
    return total


def fetch_day(token, vendor, day):
    """Return first-time downloads for one day, or 0 if no report exists."""
    params = {
        "filter[frequency]": "DAILY",
        "filter[reportSubType]": "SUMMARY",
        "filter[reportType]": "SALES",
        "filter[vendorNumber]": vendor,
        "filter[reportDate]": day,
    }
    r = requests.get(API, params=params,
                     headers={"Authorization": f"Bearer {token}", "Accept": "application/a-gzip"},
                     timeout=60)
    if r.status_code == 404:      # no sales report generated for that day
        return 0
    r.raise_for_status()
    text = gzip.decompress(r.content).decode("utf-8")
    return text


def load_stats(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {"downloads": 0, "last_report_date": None, "updated": None}


def main():
    issuer = os.environ["ASC_ISSUER_ID"]
    key_id = os.environ["ASC_KEY_ID"]
    private_key = os.environ["ASC_PRIVATE_KEY"]
    vendor = os.environ["ASC_VENDOR_NUMBER"]
    apple_id = os.environ.get("APP_APPLE_ID", "6770648419")
    release = os.environ.get("APP_RELEASE_DATE", "2026-06-04")
    stats_path = os.environ.get("STATS_PATH", "stats.json")

    stats = load_stats(stats_path)
    token = make_token(issuer, key_id, private_key)

    if stats.get("last_report_date"):
        start = dt.date.fromisoformat(stats["last_report_date"]) + dt.timedelta(days=1)
    else:
        start = dt.date.fromisoformat(release)
        stats["downloads"] = 0

    end = dt.date.today() - dt.timedelta(days=2)   # reports lag ~1-2 days
    total = stats.get("downloads", 0) or 0
    last = stats.get("last_report_date")

    day = start
    while day <= end:
        d = day.isoformat()
        try:
            text = fetch_day(token, vendor, d)
            total += parse_downloads(text, apple_id) if isinstance(text, str) else 0
            last = d
        except requests.HTTPError as e:
            print(f"warn {d}: {e}", file=sys.stderr)
        day += dt.timedelta(days=1)

    stats["downloads"] = total
    stats["last_report_date"] = last
    stats["updated"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(json.dumps(stats))


if __name__ == "__main__":
    main()
