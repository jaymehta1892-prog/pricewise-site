# Pricewise Grocery — website

Marketing site for Pricewise Grocery (free iOS grocery price-match app for the GTA).
Static site — plain HTML/CSS/JS, no build step. Hosted on GitHub Pages today; ready
to move to Cloudflare Pages + a custom domain.

## What goes where

| File / folder | Purpose |
|---|---|
| `index.html` | The entire website (self-contained). |
| `google2c173ee252db86ea.html` | Google Search Console verification — **do not delete**. |
| `robots.txt` | Allows search + AI crawlers; points to the sitemap. |
| `sitemap.xml` | Lists your homepage for search engines. |
| `llms.txt` | Plain-language summary for AI search engines. |
| `stats.json` | Download counter (starts at 0). Only used if you enable auto-downloads. |
| `assets/pricewise-icon-512.png` | App icon (used by the site's structured-data logo). |
| `scripts/update_downloads.py` | Optional: pulls real downloads from App Store Connect. |
| `.github/workflows/update-downloads.yml` | Optional: runs the above on a schedule. **Inert by default.** |
| `docs/DOWNLOADS-AUTOMATION.md` | How to turn on automatic download numbers. |
| `docs/app-store-aso.md` | App Store keyword pack (paste into App Store Connect). |
| `.gitignore` | Keeps secrets (`*.p8`) and cruft out of the repo. |

## Publishing

It's already live on GitHub Pages. **Any push to `main` redeploys automatically.**
(On Cloudflare Pages, connecting this repo gives the same push-to-deploy flow.)

## Editing common things (no tools needed)

Open `index.html` on github.com, click the **pencil** icon, edit, then **Commit** —
it redeploys in under a minute.

- **Download count:** find `var DOWNLOADS = 126;` and change the number.
- **App Store rating:** shows automatically and updates itself (pulled live from Apple).
- **Copy / headings / FAQ:** search for the text and edit it in place.

## Still to do

1. **OG share image:** add a 1200×630 image at `assets/og-image.png` (used when the link
   is shared on social). The tags already point to it.
2. **Custom domain:** once you buy it, the canonical / Open Graph / `sitemap.xml` /
   `robots.txt` URLs need to change from the GitHub Pages URL to your new domain.
   (Send the domain over and this can be updated in a couple of edits.)

## Optional: automatic download numbers

You're on a manual count right now. To make downloads update themselves from App Store
Connect, follow `docs/DOWNLOADS-AUTOMATION.md` (add 4 GitHub Secrets, then uncomment the
`schedule:` block in the workflow). It uses read-only reporting — it never creates or
submits an App Store build.
