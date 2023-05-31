from math import sin, cos, sqrt, atan2, radians, exp

import phonenumbers
import tldextract
from thefuzz import fuzz

from journo__globals.models import JournoPlaceModel, SerpResultModel, JournoSerpPlaceMatchModel
from utils.helper import load_json


def name_similar(a, b):
    return fuzz.ratio(a.lower(), b.lower()) / 100.0


def get_domain_name(domain_string):
    return tldextract.extract(domain_string).registered_domain


def get_distance(pos1: dict, pos2: dict):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(pos1['lat'])
    lon1 = radians(pos1['long'])
    lat2 = radians(pos2['lat'])
    lon2 = radians(pos2['long'])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance


def get_attribute_score(place: JournoPlaceModel, serp_place_result: dict, wof_locs: list[str]):
    # Match gid
    match_scores = {
        'distance': None,
        'address': 0,
        'phone': 0,
        'url': 0,
        'name': 0,
        'wof_overlap': None
    }

    distance = None
    if 'coordinate' in serp_place_result and place.lat and place.long:
        distance = get_distance(
            {
                "lat": place.lat,
                "long": place.long
            },
            serp_place_result['coordinate']
        )
        # Distance scoring
        score = 2 / (1 + exp(distance / 10))
        match_scores['distance'] = score

    if "title" in serp_place_result and place.name:
        match_scores['name'] = name_similar(serp_place_result['title'], place.name)

    _extraData = place.get_extra()

    if "address" in serp_place_result and "address" in _extraData:
        match_scores['address'] = name_similar(serp_place_result["address"], _extraData["address"])

    if "phone" in serp_place_result and "phone" in _extraData:
        try:
            phone_1 = phonenumbers.parse(serp_place_result["phone"], "US").national_number
            phone_2 = phonenumbers.parse(_extraData["phone"], "US").national_number
            match_scores['phone'] = 1 if phone_1 == phone_2 else 0
        except:
            match_scores['phone'] = 0

    if "url" in serp_place_result and "website" in _extraData:
        domain_1, domain_2 = get_domain_name(serp_place_result['url']), get_domain_name(_extraData['website'])
        url_score = 1 if domain_1 == domain_2 else 0
        match_scores['url'] = url_score

    res_gids = serp_place_result['gids'] if 'gids' in serp_place_result else []
    if len(wof_locs) and len(res_gids):
        # FIXME: set(wof_locs).isdisjoint(res_gids) is always FALSE,
        #  because wof_locs is list.gids and res_gids is place.gids
        #  and list.gids is [gid for gid in place for place in list.places]
        wof_overlap = not set(wof_locs).isdisjoint(res_gids)
        match_scores['wof_overlap'] = 1 if wof_overlap else 0
    else:
        match_scores['wof_overlap'] = 0.51

    comp = None
    if distance is not None:
        final_score = match_scores['distance']
        matching_criteria = 'distance'
        comp = distance
    elif match_scores['wof_overlap'] == 0:
        final_score = 0
        matching_criteria = 'mismatch_list_wof'
    elif match_scores['address']:
        final_score = match_scores['address']
        matching_criteria = 'address'
        comp = [_extraData["address"], serp_place_result["address"]]
    else:
        score_multiplier = max(
            match_scores['address'],
            match_scores['url'],
            match_scores['phone']
        )

        if score_multiplier == 0:
            score_multiplier = 1

        final_score = match_scores['name'] * score_multiplier

        matching_criteria = 'or'

    serp_place_result = {
        'score': final_score,
        'criteria': matching_criteria,
        'match_scores': match_scores,
        'wof_locs': wof_locs,
        'comp': comp
    }

    return serp_place_result


def get_match_score(place: JournoPlaceModel, place_result: dict, wof_locs: list[str]) -> dict:
    # TODO: Change distance
    '''
    1. If coordinate is available, ALWAYS use coordinate proximity

    2. If coordinate is not found, we will use alternative
        -> Address similarity (based on name, ensure that it's in the same geographical region)
        -> Phone, if the phone is identical, high probability
        -> URL, if the phone is identical, high probability of closeness
        -> Name similarity
    '''
    match_score = get_attribute_score(place, place_result, wof_locs)

    data_id = place_result['data_id']
    if 'gps_coordinates' in place_result:
        search_res = place_result['gps_coordinates']
        search_coord = {'lat': search_res['latitude'], 'long': search_res['longitude']}
    else:
        search_coord = None

    match = {
        "data_id": data_id,
        "coordinate": search_coord,
        "score": match_score['score'],
        'raw': place_result,
        'match': match_score
    }

    return match


def get_best_match(place: JournoPlaceModel, serp_result_instance: SerpResultModel, wof_locs: list[str]) -> dict[str] or None:
    # TODO: Create distance conditions based on type
    threshold = 10  # in km
    serp_result_instance_json = load_json(f"cache/serps/{serp_result_instance.result_path}")

    if 'place_results' in serp_result_instance_json:
        # If we've found the best match
        place_result = serp_result_instance_json['place_results']
        match_data = get_match_score(place, place_result, wof_locs)

        return match_data
    elif 'local_results' in serp_result_instance_json and serp_result_instance_json['local_results']:
        # If no best match was found
        local_res = serp_result_instance_json['local_results']

        potential_matches = []
        for place_result in local_res:
            if 'data_id' in place_result:
                match_data = get_match_score(place, place_result, wof_locs)
                potential_matches.append(match_data)

        if len(potential_matches) == 0:
            return None

        dists = sorted(potential_matches, key=lambda x: -x['score'])
        match_data = dists[0]  # Highest score
        return match_data

    return None


def get_place_best_match(place: JournoPlaceModel):
    serp_result_instance = SerpResultModel.objects.filter(query_key=place.serp_query).get()

    wof_locs = serp_result_instance.wof_gids

    best_match = get_best_match(place, serp_result_instance, wof_locs)
    if best_match is None:
        best_match = {'score': 0}

    best_match_query = JournoSerpPlaceMatchModel.objects.filter(place=place)

    if best_match_query.exists():
        best_match_query = best_match_query.get()
        best_match_query.score = best_match['score']

        if 'data_id' in best_match:
            best_match_query.data_id = best_match['data_id']
            del best_match['data_id']

        if 'raw' in best_match:
            del best_match['raw']

        best_match_query.best_match = best_match
        best_match_query.save()
    else:
        data_id = None

        if 'data_id' in best_match:
            data_id = best_match['data_id']
            del best_match['data_id']

        if 'raw' in best_match:
            del best_match['raw']

        JournoSerpPlaceMatchModel.objects.create(
            place=place,
            best_match=best_match,
            data_id=data_id,
            score=best_match['score']
        )
