# Skool Community & Group Scraper 🚀

Extract public Skool communities, rankings, member counts, pricing tiers, and creator metadata at scale. Built for market intelligence, creator lead generation, and competitive research on [Skool.com](https://www.skool.com).

Unlike traditional scrapers that run heavy headless browsers (Puppeteer/Playwright), this Actor uses **pure HTTP requests** to stream Next.js discovery payloads. It is **10x faster and uses 95% less compute**.

---

## 🔍 Features

- **Keyword & Topic Search:** Search for any niche (e.g., `ai`, `marketing`, `crypto`, `fitness`, `sales`).
- **Category Filtering:** Filter across all 9 official Skool categories (Tech, Money, Hobbies, Music, Health, Sports, Self-improvement, Relationships, Spirituality).
- **Price Model Filtering:** Filter specifically for `Free` communities or `Paid` subscription communities.
- **Sorting Options:** Sort results by `Trending`, `Rank`, `Total Members`, or `Newest`.
- **Zero Browser Overhead:** Runs via lightweight HTTP streams—no browser crashes, minimal RAM, and maximum speed (~3 seconds for 100 communities).
- **Export Anywhere:** Download structured data in **JSON, CSV, Excel, XML**, or sync directly to Google Sheets, Webhooks, or Make.com / Zapier.

---

## 📊 Extracted Data Fields

Each community record contains:

| Field | Type | Description |
|---|---|---|
| `name` | String | Community unique URL slug |
| `displayName` | String | Public title of the community |
| `url` | String | Direct link (`https://www.skool.com/{name}`) |
| `description` | String | Community tagline and pitch |
| `totalMembers` | Integer | Total active members count |
| `priceFormatted` | String | Formatted pricing (e.g., `$69/month`, `Free`) |
| `isFree` | Boolean | `true` if free, `false` if paid |
| `priceAmount` | Float | Numeric monthly price (e.g., `69.0`) |
| `currency` | String | Billing currency (e.g., `USD`) |
| `billingInterval` | String | Recurring period (`month` or one-time) |
| `reviewAverageRating` | Float | Average member review score (1.0 to 5.0) |
| `reviewCount` | Integer | Total public reviews count |
| `logoUrl` | String | Creator / community avatar image URL |
| `coverSmallUrl` | String | Header banner image URL |
| `rank` | Integer | Position in discovery rank |
| `createdAt` | String | Community creation timestamp |
| `updatedAt` | String | Last update timestamp |
| `scrapedAt` | String | ISO timestamp when record was collected |

---

## 🛠️ Input Configuration

| Parameter | Type | Default | Description |
|---|---|---|---|
| `searchQuery` | String | `""` | Search keyword (e.g. `ecommerce`, `trading`). Leave blank to browse all. |
| `category` | String | `"all"` | Filter by category (`tech`, `money`, `health`, etc.). |
| `price` | String | `"all"` | `"all"`, `"free"`, or `"paid"`. |
| `sort` | String | `"trending"` | `"trending"`, `"rank"`, `"members"`, or `"newest"`. |
| `maxItems` | Integer | `100` | Maximum number of communities to extract. |

### Sample Input (JSON)

```json
{
  "searchQuery": "ai",
  "category": "all",
  "price": "paid",
  "sort": "members",
  "maxItems": 100
}
```

---

## 📦 Sample Output

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
  "logoUrl": "https://assets.skool.com/f/309a463889ba441682109e263ba9e3fb/7301cd31e50247ddbb7482dfae43b9f152b9a022b39e4583999ef990935caf54",
  "createdAt": "2024-08-15T03:29:27.994705Z",
  "rank": 1
}
```

---

## ⚡ Performance & Costs

Because this Actor does not boot a browser (Chromium/Puppeteer), it consumes roughly **0.005 Compute Units (CU)** per run. Running 1,000 communities costs less than **$0.01** in platform compute.
