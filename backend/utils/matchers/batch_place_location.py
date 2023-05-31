import json
from json import JSONDecodeError

from serpapi import GoogleSearch

from journo__globals.models import SerpResultModel
from utils.helper import save_json_overwrite, slugify


def batch_place_location(query_key: str) -> (bool, str):
    params = json.loads(query_key)
    search = GoogleSearch(params)

    try:
        data = search.get_dict()
    except JSONDecodeError as e:
        return True, e

    if 'error' in data:
        return True, data['error']

    if 'search_metadata' not in data:
        return True, 'Serp does not return Search Metadata'

    if 'status' not in data['search_metadata']:
        return True, 'Serp return Search Metadata, but does not return status'

    if data['search_metadata']['status'] != "Success":
        return True, 'Serp return Search Metadata, but does not return status'

    # save to path
    filepath = params['q']
    if 'll' in params:
        filepath += f' {params["ll"]}'
    filepath = slugify(filepath)
    filepath += ".json"
    save_json_overwrite(f"cache/serps/{filepath}", data)

    SerpResultModel.objects.create(
        query_key=query_key,
        result_path=filepath
    )

    return False, None
