import asyncio
import json
import uvicorn
from fastapi import FastAPI

from config import CONFIG_FILE
from git_poller import GitPoller
from storage import Storage


storage = Storage()

gitter_app = FastAPI()

# REST API endpoints
# Returns average time [s] of event for every configured repo by event type
@gitter_app.get("/stats")
def stats():
    return storage.get_average_durations()


async def main():

    storage.load_storage()
    git_poller = GitPoller(storage)

    with open(CONFIG_FILE) as f:
        repos = json.load(f)["repos"]

    asyncio.create_task(git_poller.poll_forever(repos))

    config = uvicorn.Config(app=gitter_app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())


