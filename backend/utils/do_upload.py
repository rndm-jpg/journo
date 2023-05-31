import json
import math
import threading

import requests

from journo__globals.models import JournoPlaceModel
from utils.pretty_printer import print_primary, print_success, print_danger


def upload_media(place: JournoPlaceModel, user_id: str, headers: dict):
    def _generate_media_url(_image_url, _attribution):
        response = requests.request(
            "POST",
            url="http://10.129.15.231:3000/_internal/import/media/url",
            json={
                "url": _image_url,
                "userId": user_id,
                # Very important that this matches the user the list / note is being attached to
                # In the future we will be verifying this and filtering out bad access
                "attribution": _attribution
            },
            headers=headers
        ).json()
        return response

    if place.media and not place.mediaIds:
        place.mediaIds = []
        for raw_media in place.media:
            if 'url' in raw_media:
                place.mediaIds.append(
                    _generate_media_url(
                        _image_url=raw_media['url'],
                        _attribution=raw_media['credit'] if 'credit' in raw_media else place.externalAttribution
                    )
                )

        place.save()


def upload_postcard(place: JournoPlaceModel, user_id: str, headers: dict):
    def _create_placenote(raw_placenote: dict):
        response = requests.request(
            "POST",
            url="http://10.129.15.231:3000/_internal/import/note",
            json={
                "userId": user_id,
                "placeNote": raw_placenote
            },
            headers=headers,
            timeout=30,
        ).json()

        return response

    if not place.pc_upload_result:
        try:
            upload_result = _create_placenote(
                raw_placenote=place.jsonified()
            )
            place.set_uploaded(upload_result)

        except Exception as e:
            print(e)
            if place.pc_upload_result:
                place.pc_upload_result = None
                place.uploadedAt = None
                place.save()


def do_upload_places(places: list[JournoPlaceModel], user_id: str, headers: dict):
    for place in places:
        upload_media(place, user_id, headers)
        upload_postcard(place, user_id, headers)
