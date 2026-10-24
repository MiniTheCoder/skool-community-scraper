# Skool Community Scraper

[![Run on Apify](https://apify.com/actor-badge?actor=fastdata_lab/skool-community-scraper)](https://apify.com/fastdata_lab/skool-community-scraper)

Extracts public community data from Skool's discovery directory without requiring a login or browser automation.

[**Run directly on Apify Store**](https://apify.com/fastdata_lab/skool-community-scraper) — zero installation required.

## What it does

This Actor queries Skool's public discovery portal (`skool.com/discovery`) and parses the server-rendered Next.js payload directly. It extracts group metadata, member counts, pricing tiers, and rankings.

Because it uses HTTP requests instead of a headless browser (Puppeteer/Playwright), runs complete in 3–5 seconds and consume negligible compute ($0.001 per run).

## Extracted data

For each community, the actor outputs:

- `name`: URL slug (e.g. `filmmaking` -> `skool.com/filmmaking`)
- `displayName`: Public community name
- `url`: Direct link to the community
- `description`: Tagline / bio
- `totalMembers`: Total registered members
- `priceFormatted`: Human-readable price (e.g. `$69/month` or `Free`)
- `isFree`: Boolean flag
- `priceAmount`: Numerical amount (in USD)
- `currency`: Billing currency
- `billingInterval`: `month`, `year`, or one-time
- `reviewAverageRating`: Rating (1.0 to 5.0)
- `reviewCount`: Total member reviews
- `rank`: Position in Skool discovery ranking
- `logoUrl`: Avatar image
- `coverSmallUrl`: Banner image
- `createdAt` / `updatedAt`: ISO timestamps

## Input parameters

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `searchQuery` | string | `""` | Search keyword (e.g. `marketing`, `ai`, `trading`) |
| `category` | string | `"all"` | `tech`, `money`, `hobbies`, `music`, `health`, `sports`, `self_improvement`, `relationships`, `spirituality` |
| `price` | string | `"all"` | `all`, `free`, or `paid` |
| `sort` | string | `"trending"` | `trending`, `rank`, `members`, or `newest` |
| `maxItems` | integer | `100` | Maximum records to return |

## Example output

```json
{
  "id": "309a463889ba441682109e263ba9e3fb",
  "name": "filmmaking",
  "displayName": "Ai Filmmaking",
  "url": "https://www.skool.com/filmmaking",
  "description": "Currently: $7/mo. Master AI Filmmaking. The Formula to Retain & Convert Anyone! No Gatekeeping.",
  "totalMembers": 6015,
  "priceFormatted": "$7/month",
  "isFree": false,
  "priceAmount": 7.0,
  "currency": "USD",
  "billingInterval": "month",
  "reviewAverageRating": 5.0,
  "reviewCount": 27,
  "rank": 1,
  "scrapedAt": "2026-10-22T15:08:11Z"
}
```

## Limitations

- Only extracts public community metadata from the discovery directory.
- Does not scrape private posts, course classroom modules, or member lists behind a paid login wall.
