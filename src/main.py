"""
Skool Community & Group Scraper (Apify Actor)
Extracts structured community data from Skool's public discovery portal with zero browser overhead.
"""

import asyncio
from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from apify import Actor
import httpx

DISCOVERY_URL = "https://www.skool.com/discovery"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


def parse_price(display_price_raw: Optional[str]) -> Dict[str, Any]:
    """Parses the nested JSON string in displayPrice into readable fields."""
    if not display_price_raw:
        return {
            "priceFormatted": "Free",
            "isFree": True,
            "currency": None,
            "amount": 0.0,
            "recurringInterval": None,
        }

    try:
        data = json.loads(display_price_raw)
        currency = data.get("currency", "usd").upper()
        raw_amount = data.get("amount", 0)
        amount = raw_amount / 100.0 if isinstance(raw_amount, (int, float)) else 0.0
        interval = data.get("recurring_interval", "month")

        symbol = "$" if currency == "USD" else f"{currency} "
        if interval:
            formatted = f"{symbol}{amount:.2f}/{interval}".replace(".00/", "/")
        else:
            formatted = f"{symbol}{amount:.2f}".replace(".00", "")

        return {
            "priceFormatted": formatted,
            "isFree": amount == 0,
            "currency": currency,
            "amount": amount,
            "recurringInterval": interval,
        }
    except Exception:
        return {
            "priceFormatted": str(display_price_raw),
            "isFree": False,
            "currency": None,
            "amount": None,
            "recurringInterval": None,
        }


def clean_group_record(item: Dict[str, Any], rank_idx: int) -> Dict[str, Any]:
    """Transforms raw Next.js group item into clean structured output."""
    g = item.get("group", {}) or {}
    meta = g.get("metadata", {}) or {}

    price_info = parse_price(meta.get("displayPrice"))
    group_name = g.get("name", "")

    return {
        "id": g.get("id"),
        "name": group_name,
        "displayName": meta.get("displayName") or group_name,
        "url": f"https://www.skool.com/{group_name}" if group_name else None,
        "description": meta.get("description", ""),
        "totalMembers": meta.get("totalMembers", 0),
        "priceFormatted": price_info["priceFormatted"],
        "isFree": price_info["isFree"],
        "priceAmount": price_info["amount"],
        "currency": price_info["currency"],
        "billingInterval": price_info["recurringInterval"],
        "reviewAverageRating": (
            float(meta.get("reviewAverageRating"))
            if meta.get("reviewAverageRating")
            else None
        ),
        "reviewCount": meta.get("reviewCount", 0),
        "membershipModel": meta.get("membershipModel"),
        "color": meta.get("color"),
        "initials": meta.get("initials"),
        "logoUrl": meta.get("logoUrl"),
        "coverSmallUrl": meta.get("coverSmallUrl"),
        "createdAt": g.get("createdAt"),
        "updatedAt": g.get("updatedAt"),
        "rank": item.get("rank", rank_idx),
        "tags": item.get("tags") or [],
        "scrapedAt": datetime.now(timezone.utc).isoformat(),
    }


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}

        search_query = actor_input.get("searchQuery", "").strip()
        category = actor_input.get("category", "all")
        price_filter = actor_input.get("price", "all")
        sort_by = actor_input.get("sort", "trending")
        max_items = int(actor_input.get("maxItems", 100))

        Actor.log.info(
            f"Starting Skool Scraper: query='{search_query}', category='{category}', "
            f"price='{price_filter}', sort='{sort_by}', maxItems={max_items}"
        )

        headers = {
            "User-Agent": DEFAULT_USER_AGENT,
        }

        # Optional proxy configuration
        proxy_config = actor_input.get("proxyConfiguration")
        proxy_url = None
        if proxy_config and proxy_config.get("useApifyProxy"):
            proxy_url_obj = await Actor.create_proxy_configuration(actor_proxy_input=proxy_config)
            if proxy_url_obj:
                proxy_url = await proxy_url_obj.new_url()

        client_kwargs = {
            "headers": headers,
            "timeout": 20.0,
            "follow_redirects": True,
        }
        if proxy_url:
            client_kwargs["proxy"] = proxy_url

        items_scraped = 0
        page = 1
        seen_ids = set()

        async with httpx.AsyncClient(**client_kwargs) as client:
            while items_scraped < max_items:
                params: Dict[str, Any] = {"p": page}
                if search_query:
                    params["q"] = search_query
                if category and category != "all":
                    params["category"] = category
                if price_filter and price_filter != "all":
                    params["price"] = price_filter
                if sort_by and sort_by != "trending":
                    params["sort"] = sort_by

                Actor.log.info(f"Fetching page {page} with params: {params}...")

                try:
                    resp = await client.get(DISCOVERY_URL, params=params)
                    if resp.status_code != 200:
                        Actor.log.warning(
                            f"Page {page} returned status code {resp.status_code}. Stopping pagination."
                        )
                        break

                    text = resp.text
                    start_tag = '<script id="__NEXT_DATA__" type="application/json">'
                    if start_tag not in text:
                        Actor.log.warning("No __NEXT_DATA__ found in response. Skool response format may have changed.")
                        break

                    start_idx = text.find(start_tag) + len(start_tag)
                    end_idx = text.find("</script>", start_idx)
                    raw_json = text[start_idx:end_idx]
                    page_data = json.loads(raw_json)

                    page_props = page_data.get("props", {}).get("pageProps", {})
                    groups = page_props.get("groups", [])

                    if not groups:
                        Actor.log.info(f"No groups returned on page {page}. Reached end of results.")
                        break

                    batch_to_push: List[Dict[str, Any]] = []
                    for idx, group_item in enumerate(groups):
                        if items_scraped >= max_items:
                            break

                        record = clean_group_record(group_item, (page - 1) * 30 + idx + 1)
                        group_id = record.get("id")

                        if group_id and group_id in seen_ids:
                            continue
                        if group_id:
                            seen_ids.add(group_id)

                        batch_to_push.append(record)
                        items_scraped += 1

                    if batch_to_push:
                        await Actor.push_data(batch_to_push)
                        Actor.log.info(
                            f"Pushed {len(batch_to_push)} groups (Total scraped: {items_scraped}/{max_items})"
                        )

                    # Check if there are more pages
                    has_more = page_props.get("hasMore", False)
                    num_groups = page_props.get("numGroups")

                    # If page returned fewer than 30 items or reached end
                    if len(groups) < 30:
                        Actor.log.info("Page returned fewer than 30 groups; end of results reached.")
                        break

                    page += 1
                    # Polite sleep between requests
                    await asyncio.sleep(0.4)

                except Exception as e:
                    Actor.log.error(f"Error fetching page {page}: {e}")
                    break

        Actor.log.info(f"Scrape completed successfully. Total unique communities saved: {items_scraped}.")


if __name__ == "__main__":
    asyncio.run(main())
