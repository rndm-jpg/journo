import ast
import csv
import os
from uuid import uuid4

import numpy as np
import pandas as pd
from scipy.spatial import KDTree

from journo__globals.models import SerpResultModel
from utils.helper import load_json, save_json_overwrite


# Take all gids whos key ends with _gid from wof result
def get_location_gids(wof_result: dict[str]) -> list[str]:
    if wof_result is None:
        return []

    location_gids = []
    prop_keys = filter(lambda x: x.endswith("_gid"), [k for k in wof_result.keys()])
    location_gids.extend([wof_result[pk] for pk in prop_keys])
    location_gids = list(filter(lambda x: type(x) == str, location_gids))
    return location_gids


def append_wof_gids_to_serpapi_result(serp_result_instance: SerpResultModel):
    serp_result_instance_json = load_json(f"cache/serps/{serp_result_instance.result_path}")

    gids = []
    if 'local_results' in serp_result_instance_json:
        for sp in serp_result_instance_json['local_results']:
            gids.extend(
                get_location_gids(sp['wof'])
            )
            sp['gids'] = gids

    elif 'place_results' in serp_result_instance_json and len(serp_result_instance_json['place_results']):
        gids = get_location_gids(serp_result_instance_json['place_results']['wof'])
        serp_result_instance_json['place_results']['gids'] = gids

    serp_result_instance.wof_gids = gids
    serp_result_instance.save()
    save_json_overwrite(f"cache/serps/{serp_result_instance.result_path}", serp_result_instance_json)


def get_closest_match(pos, kdtree, wof_results_with_coord, show=False):
    target_coord = np.array([pos['latitude'], pos['longitude']])
    distance, idx = kdtree.query(target_coord)

    if distance > 10 or idx < 0 or idx >= len(wof_results_with_coord):
        return None

    return wof_results_with_coord[idx]


def append_each_wof_result_to_serpapi_result(serp_result_instance: SerpResultModel, wof_result: list[dict[str]]):
    # Create an np array with lat and lon from wof_result
    np_coords = np.array(
        [
            [c['lat'], c['lon']] for c in wof_result
        ]
    )

    # Prepare KDTree
    kdtree = KDTree(np_coords)

    if serp_result_instance.isWOF:
        return

    serp_result_instance_json = load_json(f"cache/serps/{serp_result_instance.result_path}")

    if 'local_results' in serp_result_instance_json:
        for lr in serp_result_instance_json['local_results']:
            closest_match = None
            if 'gps_coordinates' in lr:
                closest_match = get_closest_match(
                    lr['gps_coordinates'],
                    kdtree,
                    wof_result
                )

            lr['wof'] = closest_match

    elif 'place_results' in serp_result_instance_json:
        closest_match = get_closest_match(
            serp_result_instance_json['place_results']['gps_coordinates'],
            kdtree,
            wof_result
        )
        serp_result_instance_json['place_results']['wof'] = closest_match

    serp_result_instance.isWOF = True
    serp_result_instance.save()

    save_json_overwrite(f"cache/serps/{serp_result_instance.result_path}", serp_result_instance_json)


def get_wof_list(serp_result_instance: SerpResultModel, df):
    # Column title
    columns: list[str] = [column for column in df]

    # Convert CSV to JSON.
    wof_results: list[dict[str]] = []
    for _, row in df.iterrows():
        wof_data: dict[str] = {}

        for column in columns:
            key = column.replace("ge:", "")
            value = row[column]
            wof_data[key] = value

        wof_results.append(wof_data)

    # Connect Serpapi Result to WOF result
    append_each_wof_result_to_serpapi_result(serp_result_instance, wof_results)

    # Connect WOF result to Place
    append_wof_gids_to_serpapi_result(serp_result_instance)


def fetch_wof_result_for_serpapi_result(serp_result_instance: SerpResultModel):
    # This function doesn't run on Windows
    if os.name == 'nt':
        raise NotImplementedError("This function can't run on Windows")

    # Generate temporary file
    process_id = uuid4()
    LIST_FILE_PATH = f"cache/{process_id}.csv"
    RESULT_FILE_PATH = f"cache/{process_id}_result.csv"

    location_place_to_search = {}
    serp_result_instance_json = load_json(f"cache/serps/{serp_result_instance.result_path}")

    coords = []
    if 'local_results' in serp_result_instance_json:
        coords = []
        for local_result in serp_result_instance_json['local_results']:
            if 'gps_coordinates' in local_result:
                coords.append(local_result['gps_coordinates'])

    elif 'place_results' in serp_result_instance_json:
        coords = [serp_result_instance_json['place_results']['gps_coordinates']]

    for c in coords:
        location_place_to_search[str(c)] = True

    location_place_to_search = [key for key in location_place_to_search]

    # open the file in the write mode
    with open(LIST_FILE_PATH, 'w') as f:
        # create the csv writer
        writer = csv.writer(f)

        writer.writerow(["lat", "lon"])

        for i, str_loc in enumerate(location_place_to_search):
            loc = ast.literal_eval(str_loc)
            # write a row to the csv file
            writer.writerow([loc["latitude"], loc["longitude"]])

        f.close()

    os.environ['GE_API_KEY'] = ""
    os.system(
        "ge batch csv --endpoint '/v1/reverse' -p 'sources' -t 'wof' -p 'point.lat' -t '${row.lat}' -p 'point.lon' -t '${row.lon}' -p 'layers' -t 'coarse' " + LIST_FILE_PATH + " > " + RESULT_FILE_PATH
    )

    df = pd.read_csv(RESULT_FILE_PATH)

    get_wof_list(
        serp_result_instance,
        df,
    )

    os.remove(LIST_FILE_PATH)
    os.remove(RESULT_FILE_PATH)
