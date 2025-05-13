import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, Deque, List, Tuple

from config import STORAGE_FILE, DATE_FORMAT, MAX_DAYS, MAX_EVENTS


# Takes care of storing events in memory, and saving/loading from disk
class Storage:
    def __init__(self):
        # In-memory cache of events
        self.event_store: Dict[str, Deque[Tuple[str, str, datetime]]] = defaultdict(deque)

    def id_exists(self, repo_name: str, event_id: str):
        return any(eid == event_id for eid, _, _ in self.event_store[repo_name])

    # Load events from STORAGE_FILE and keep in event_store cache
    def load_storage(self) -> None:
        if not os.path.exists(STORAGE_FILE):
            return

        with open(STORAGE_FILE, "r") as f:
            data = json.load(f)

        print(f"Loading storage from {STORAGE_FILE}")
        for repo, events in data.items():
            for event_id, event_type, created_at_str in events:
                created_at = datetime.strptime(created_at_str, DATE_FORMAT)
                self.add_event(repo, event_id, event_type, created_at)

    # Save current event_store cache to pernament STORAGE_FILE
    def save_storage(self) -> None:
        data = {
            repo: [(event_id, event_type, dt.strftime(DATE_FORMAT)) for event_id, event_type, dt, in events]
            for repo, events in self.event_store.items()
        }

        print(f"Saving storage to {STORAGE_FILE}")
        with open(STORAGE_FILE, "w") as f:
            json.dump(data, f)

    def event_too_old(self, created_at: datetime) -> bool:
        cutoff_date = datetime.utcnow() - timedelta(days=MAX_DAYS)
        return created_at < cutoff_date

    # Add an event to the cache
    def add_event(self, repo_name: str, event_id: str, event_type: str, created_at: datetime):
        self.event_store[repo_name].append((event_id, event_type, created_at))

    # Remove out dated / out of max count  events
    def prune_store(self, repo: str) -> None:
        repo_events = self.event_store[repo]

        # Prune by date
        while repo_events and self.event_too_old(repo_events[0][2]):
            repo_events.popleft()

        # Prune by count
        while len(repo_events) > MAX_EVENTS:
            repo_events.popleft()

    # Returns dictionary for every repo with average event type time delta [s]
    def get_average_durations(self) -> Dict[str, Dict[str, float]]:
        result = {}
        for repo, events in self.event_store.items():
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

