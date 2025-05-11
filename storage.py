import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, Deque, List, Tuple

from config import STORAGE_FILE, DATE_FORMAT, MAX_DAYS, MAX_EVENTS

# In-memory cache of events
event_store: Dict[str, Deque[Tuple[str, str, datetime]]] = defaultdict(deque)
event_ids: Dict[str, set] = defaultdict(set)


# Load events from STORAGE_FILE and keep in event_store cache
def load_storage() -> None:
    if not os.path.exists(STORAGE_FILE):
        return

    with open(STORAGE_FILE, "r") as f:
        data = json.load(f)

    for repo, events in data.items():
        for event_id, event_type, created_at_str in events:
            created_at = datetime.strptime(created_at_str, DATE_FORMAT)
            event_store[repo].append((event_id, event_type , created_at))
            event_ids[repo].add(event_id)

# Save current event_store cache to pernament STORAGE_FILE
def save_storage() -> None:
    data = {
        repo: [(event_id, event_type, dt.strftime(DATE_FORMAT)) for event_id, event_type, dt, in events]
        for repo, events in event_store.items()
    }

    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f)


# Save event to the cache, remove out dated / out of limit events
# Updates STORAGE_FILE
def prune_and_update(repo: str, event: dict) -> None:
    event_type = event.get("type")
    created_at_str = event.get("created_at")

    event_id = event.get("id")
    if not event_type or not created_at_str or not event_id:
        return

    # Skip duplicates
    if event_id in event_ids[repo]:
        return

    event_ids[repo].add(event_id)

    created_at = datetime.strptime(created_at_str, DATE_FORMAT)
    store = event_store[repo]
    store.append((event_id, event_type, created_at))

    # Prune by date
    cutoff = datetime.utcnow() - timedelta(days=MAX_DAYS)
    while store and store[0][2] < cutoff:
        store.popleft()

    # Prune by max count
    while len(store) > MAX_EVENTS:
        store.popleft()

    save_storage()


# Returns dictionary for every repo with average event type time delta
def get_average_durations() -> Dict[str, Dict[str, float]]:
    result = {}
    for repo, events in event_store.items():
        by_type: Dict[str, List[datetime]] = defaultdict(list)

        for event_id, event_type, created_at in events:
            by_type[event_type].append(created_at)

        result[repo] = {}

        for event_type, timestamps in by_type.items():
            if len(timestamps) < 2:
                result[repo][event_type] = 0.0
                continue

            timestamps.sort()
            gaps = [
                (t2 - t1).total_seconds()
                for t1, t2 in zip(timestamps[:-1], timestamps[1:])
            ]
            result[repo][event_type] = sum(gaps) / len(gaps)

    return result
