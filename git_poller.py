import asyncio
import os

import aiohttp
from datetime import datetime, timedelta
from typing import List

from config import GITHUB_API_URL, MAX_EVENTS, MAX_DAYS, POLL_INTERVAL, DATE_FORMAT
from storage import prune_and_update, event_ids

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def parse_github_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, DATE_FORMAT)


# Request events for the given repo, paginated
async def get_event_page(session: aiohttp.ClientSession, repo: str, page: int):
    url = f"{GITHUB_API_URL.format(repo)}?per_page=100&page={page}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "gitter",
        "Authorization": f"Bearer {GITHUB_TOKEN}" if GITHUB_TOKEN else None
    }
    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            print(f"GitHub returned: {response.status}.")
            return None

        return await response.json()


# Returns true if the event count does not exceed MAX_EVENTS limit,
# and event date was within MAX_DAYS
def should_process_event(created_at: datetime, count: int) -> bool:
    cutoff_date = datetime.utcnow() - timedelta(days=MAX_DAYS)
    return created_at >= cutoff_date and count < MAX_EVENTS


# Fetch events for given repo
async def fetch_events(session: aiohttp.ClientSession, repo: str) -> None:
    events_count = 0
    page = 1

    while events_count < MAX_EVENTS:
        events = await get_event_page(session, repo, page)
        if not events:
            break

        for event in events:
            # event already in storage, no need to load further
            event_id = event.get("id")
            if event_id in event_ids[repo]:
                return

            created_at = parse_github_date(event["created_at"])
            # We reached count/date limit
            if not should_process_event(created_at, events_count):
                return

            prune_and_update(repo, event)
            events_count += 1

        page += 1


# Runs GitHub poller forever - querying events of configured repos in POLL_INTERVAL
async def poll_forever(repos_list: List[str]) -> None:
    while True:
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_events(session, repo) for repo in repos_list]
            await asyncio.gather(*tasks)

        await asyncio.sleep(POLL_INTERVAL)
