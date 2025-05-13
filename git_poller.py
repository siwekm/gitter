import asyncio
import os
import aiohttp
from datetime import datetime
from typing import List

from config import GITHUB_API_URL, MAX_EVENTS, POLL_INTERVAL, DATE_FORMAT


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def parse_github_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, DATE_FORMAT)


# Takes care of requesting events from GitHub API
class GitPoller:

    def __init__(self, storage):
        self.storage = storage

    # Request events for the given repo, paginated
    async def get_event_page(self, session: aiohttp.ClientSession, repo: str, page: int):
        url = f"{GITHUB_API_URL.format(repo)}?per_page=100&page={page}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "gitter",
        }

        if GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

        print(f"Fetching events for repo: {repo}, page: {page}")
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                print(f"GitHub returned: {response.status}.")
                return None

            return await response.json()

    # Fetch events for given repo
    async def fetch_events(self, session: aiohttp.ClientSession, repo: str) -> None:
        events_count = 0
        page = 1

        while events_count < MAX_EVENTS:
            events = await self.get_event_page(session, repo, page)
            if not events:
                break

            for event in events:
                event_id = event.get("id")
                created_at_str = event.get("created_at")
                event_type = event.get("type")

                if not event_id or not created_at_str or not event_type:
                    continue  # Skip invalid entries

                if self.storage.id_exists(repo, event_id):
                    return  # Assume earlier events are already loaded

                created_at = datetime.strptime(created_at_str, DATE_FORMAT)
                if not created_at or self.storage.event_too_old(created_at):
                    continue  # Skip old entries

                self.storage.add_event(repo, event_id, event_type, created_at)
                events_count += 1

                self.storage.prune_store(repo)

                events_count += 1

            page += 1

        self.storage.save_storage()

    # Runs GitHub poller forever - querying events of configured repos in POLL_INTERVAL
    async def poll_forever(self, repos_list: List[str]) -> None:
        while True:
            async with aiohttp.ClientSession() as session:
                tasks = [self.fetch_events(session, repo) for repo in repos_list]
                await asyncio.gather(*tasks)

            await asyncio.sleep(POLL_INTERVAL)
