# Repos to query
CONFIG_FILE = "config_repos.json"
GITHUB_API_URL = "https://api.github.com/repos/{}/events"
POLL_INTERVAL = 300
# How many events per repo should be kept at max
MAX_EVENTS = 500
# How many days of events should be kept at max
MAX_DAYS = 70
# Permanent storage with events
STORAGE_FILE = "event_storage.json"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"