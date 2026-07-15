# Automatic download counter — setup (one time, ~10 min)

Apple doesn't publish download counts publicly, so this pulls your **real** numbers
from the App Store Connect API on a schedule and writes them to `stats.json`, which
the website reads. Your keys live only in **GitHub Secrets** — never in the code.

## Files (put them in your `pricewise-site` repo)
- `scripts/update_downloads.py`  — the fetcher
- `.github/workflows/update-downloads.yml` — runs it daily + commits `stats.json`
- `stats.json` — starts at 0; the workflow fills it in
- `index.html` — already reads `stats.json` and shows "N+ downloads" when it's > 0

> `stats.json` and `index.html` must sit in the **same folder** (your site root). If your
> Pages site is served from `/docs`, move `stats.json` there and set `STATS_PATH=docs/stats.json`
> in the workflow `env`.

## 1) Create an App Store Connect API key
App Store Connect → **Users and Access → Integrations → App Store Connect API** → **(+)**.
- Give it a name, role **Finance** (or Admin), Generate.
- Copy the **Issuer ID** and the new key's **Key ID**.
- **Download the `.p8` private key** (you can only download it once).

## 2) Find your Vendor Number
App Store Connect → **Payments and Financial Reports** → it's shown top-left
(an 8-digit number).

## 3) Add 4 repository Secrets
Repo → **Settings → Secrets and variables → Actions → New repository secret**:
| Secret name | Value |
|---|---|
| `ASC_ISSUER_ID` | the Issuer ID |
| `ASC_KEY_ID` | the Key ID |
| `ASC_PRIVATE_KEY` | paste the **entire** contents of the `.p8` file, including the `-----BEGIN/END PRIVATE KEY-----` lines |
| `ASC_VENDOR_NUMBER` | your vendor number |

**Never commit the `.p8` file itself.** Add `*.p8` to `.gitignore`.

## 4) Run it
Repo → **Actions → "Update download count" → Run workflow** (first run back-fills from
your release date; it can take a minute). After that it runs automatically every day.
The hero will show "N+ downloads" as soon as `stats.json` has a number above 0.

## Notes
- Counts **first-time downloads** (installs), not updates or re-downloads. If you'd rather
  count something else, edit `FIRST_DOWNLOAD_PTI` in the script.
- Apple's daily reports lag ~1–2 days, so the number trails real-time slightly.
- If you'd prefer not to run this, you can instead set `var DOWNLOADS = 5000;` in `index.html`
  and update it by hand whenever you like.
