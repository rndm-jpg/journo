from journo__globals.models import JournoPlaceModel

serpapi_api_key = ""


def generate_serp_query(place: JournoPlaceModel):
    _extraData = place.get_extra()

    address = None
    if 'address' in _extraData:
        address = _extraData['address']

        address_comma = address.split(", ")
        if len(address_comma) > 3:
            address = ", ".join(address_comma[:3])

    q = f'"{place.name}" '
    if address:
        q = f"{q} {address}"

    params = {
        "api_key": serpapi_api_key,
        "engine": "google_maps",
        "q": q,
        "google_domain": "google.com",
    }

    if place.lat and place.long:
        params['ll'] = f"@{round(place.lat, 7)},{round(place.long, 7)},14z"

    return params
