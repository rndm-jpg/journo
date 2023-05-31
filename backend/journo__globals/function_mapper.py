import json
import math
import threading

import requests

from journo__globals.models import JournoPlaceModel, SourceModel, JournoFlowModel
from src.eater__structured.eater__structured import EaterStructured
from utils.do_match import do_match_places
from utils.do_upload import do_upload_places
from utils.pretty_printer import print_primary

def get_access_token():
    response = requests.request(
        "POST",
        url="https://auth.postcard.inc/oauth/token",
        json={
            "client_id": "",
            "client_secret": "",
            "audience": "https://import.postcard.inc",
            "grant_type": "client_credentials"
        },
        headers={
            'content-type': "application/json"
        }
    )

    return json.loads(response.text)["access_token"]


def do_crawl(source: str, flow=None):
    if source == 'EATER__STRUCTURED':
        EaterStructured.crawl(flow)


def do_parse(source: str):
    if source == 'EATER__STRUCTURED':
        EaterStructured.parse()


def do_match(source: str, score_threshold=0.5):
    places = JournoPlaceModel.objects.filter(
        ignoredAt__isnull=True,
        matchedAt__isnull=True,
        page__source__name=source
    )

    THREAD_LIMIT = 30

    total_item = places.count()

    places = [x for x in places]

    threads = []

    for thread_number in range(THREAD_LIMIT):
        start_idx = math.floor(thread_number * total_item / THREAD_LIMIT)
        end_idx = math.floor((thread_number + 1) * total_item / THREAD_LIMIT)
        focused_places = places[start_idx:end_idx]
        threads.append(
            threading.Thread(
                target=do_match_places,
                args=(
                    focused_places,
                    score_threshold
                )
            )
        )

    for thread_item in threads:
        thread_item.start()

    for thread_item in threads:
        thread_item.join()


def do_upload(source: str, pcuser_id: str):
    headers = {
        'content-type': "application/json",
        'Authorization': f"Bearer {get_access_token()}"
    }

    places = JournoPlaceModel.objects.filter(
        ignoredAt__isnull=True,
        pc_upload_result__isnull=True,
        page__source__name=source
    )

    THREAD_LIMIT = 30

    total_item = places.count()

    places = [x for x in places]

    threads = []

    for thread_number in range(THREAD_LIMIT):
        start_idx = math.floor(thread_number * total_item / THREAD_LIMIT)
        end_idx = math.floor((thread_number + 1) * total_item / THREAD_LIMIT)
        focused_places = places[start_idx:end_idx]
        threads.append(
            threading.Thread(
                target=do_upload_places,
                args=(
                    focused_places,
                    pcuser_id,
                    headers
                )
            )
        )

    for thread_item in threads:
        thread_item.start()

    for thread_item in threads:
        thread_item.join()


def do_flow(pfh: JournoFlowModel, source: SourceModel):
    print_primary(f"{source.name} Flow", "Crawling...")
    do_crawl(
        source=source.name,
        flow=pfh
    )

    print_primary(f"{source.name} Flow", "Parsing...")
    do_parse(
        source=source.name,
    )

    print_primary(f"{source.name} Flow", "Matching...")
    do_match(
        source=source.name,
        score_threshold=source.score_threshold
    )

    print_primary(f"{source.name} Flow", "Writing Successes!")
    print_primary(f"{source} Flow", "Done!")
