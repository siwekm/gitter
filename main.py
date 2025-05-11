import asyncio
import json
import uvicorn
from multiprocessing import Process

from config import CONFIG_FILE
from git_poller import poll_forever
from api import gitter_app


def start_api():
    uvicorn.run(gitter_app, host="0.0.0.0", port=8001)


def start_poller(repos_to_poll):
    asyncio.run(poll_forever(repos_to_poll))


if __name__ == "__main__":
    with open(CONFIG_FILE) as f:
        repos = json.load(f)["repos"]

    api_process = Process(target=start_api)
    poller_process = Process(target=start_poller, args=(repos,))

    api_process.start()
    poller_process.start()

    api_process.join()
    poller_process.join()
