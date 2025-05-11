from fastapi import FastAPI
from storage import get_average_durations, load_storage

gitter_app = FastAPI()


@gitter_app.get("/stats")
def stats():
    load_storage()
    return get_average_durations()