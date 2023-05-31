from journo__globals.models import JournoPlaceModel
import spacy

nlp = spacy.load("en_core_web_trf")


def enrich_location(place: JournoPlaceModel) -> JournoPlaceModel or None:
    page = place.page
    if page.ignoredAt is not None:
        return

    if page.locations:
        return place

    locations = []

    if page.title:
        entities = [e for e in nlp(str(page.title)).ents]
        locs = []
        for en in entities:
            if en.label_ == "GPE":
                locs.append(en.text)
        locations.extend(locs)

    if page.description:
        entities = [e for e in nlp(str(page.description)).ents]
        locs = []
        for en in entities:
            if en.label_ == "GPE":
                locs.append(en.text)
        locations.extend(locs)

    page.locations = locations
    page.save()
