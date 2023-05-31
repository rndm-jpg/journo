import base64
import json

import pandas as pandas

from journo__globals.models import JournoPlaceModel, SerpResultModel, JournoSerpPlaceMatchModel
from utils.matchers.batch_place_location import batch_place_location
from utils.matchers.enrich_location import enrich_location
from utils.matchers.generate_serp_query import generate_serp_query
from utils.matchers.statistics import get_place_best_match
from utils.matchers.wof_list_location import fetch_wof_result_for_serpapi_result
from utils.pretty_printer import print_primary


def pc_encode(raw_string):
    return "".join(map(chr, base64.b64encode(raw_string.encode('ascii')).rstrip(b'=')))


def best_match_to_pc(best_match: JournoSerpPlaceMatchModel):
    latitude, longitude = best_match.best_match['coordinate']['lat'], best_match.best_match['coordinate']['long']
    data_string = "!4m5!3m4!1s" + best_match.data_id + "!8m2!3d" + str(latitude) + "!4d" + str(longitude)

    return pc_encode("sa|" + data_string)


def do_match_places(places: list[JournoPlaceModel], score_threshold=0.5):
    for place in places:
        source = place.page.source.name
        print_primary(f"{source} => Matching", place.name)

        # Enrich location name if JournoPage doesn't have such attribute
        if not place.page.locations:
            enrich_location(place)
            place.refresh_from_db()

        # Generate serpapi query for this JournoPlace if it doesn't exist
        if not place.serp_query:
            serpapi_params = generate_serp_query(place)
            place.serp_query = json.dumps(serpapi_params)
            place.save()

        # Fetch serpapi if it doesn't exist
        serp_result_instance = SerpResultModel.objects.filter(query_key=place.serp_query)
        if not serp_result_instance.exists():
            error, error_message = batch_place_location(place.serp_query)
            if error:
                place.set_ignored(f"SERP: {error_message}")
                continue

        # Get WOF result for Serp Result (gids), if it doesn't exist yet
        serp_result_instance = SerpResultModel.objects.filter(query_key=place.serp_query).get()
        if not serp_result_instance.wof_gids or not serp_result_instance.isWOF:
            try:
                fetch_wof_result_for_serpapi_result(serp_result_instance)
                serp_result_instance.refresh_from_db()
            except pandas.errors.EmptyDataError:
                place.set_ignored("WOF ERROR: Serp Result Return 0 Coordinate, can't proceed")
                continue

        # Get Place's Best Match if it doesn't exist
        place_best_match = JournoSerpPlaceMatchModel.objects.filter(place=place)
        if not place_best_match.exists():
            get_place_best_match(place)
        best_match_instance = JournoSerpPlaceMatchModel.objects.filter(place=place).get()

        # Finally, generate placeId
        place.placeId = best_match_to_pc(best_match_instance)

        # Filter the place if it does not pass the score threshold
        score = best_match_instance.score
        if score < score_threshold:
            place.set_ignored(f"Score is lower than threshold: {score} < {score_threshold}")
            continue

        # Ensure the place has a description
        if not place.description:
            place.description = place.excerpt if place.excerpt else place.name

        place.set_matched()
