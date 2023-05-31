import json

from journo__globals.models import JournoPageModel, JournoPlaceModel, JournoFlowModel
from src.eater__structured import eater_utils
from src.generic_source import GenericSource
from utils.helper import fetch_until_success, fetch_with_cache


class EaterStructured(GenericSource):
    source_name = "EATER__STRUCTURED"

    @staticmethod
    def crawl(flow: JournoFlowModel = None):
        # Loop from page 1 to page 10
        limit = 100
        for i in range(0, limit):
            # Fetch
            EaterStructured.print_primary(EaterStructured.source_name, "Crawling", f"Page {i:02d} of {limit:02d}")
            soup = fetch_until_success(f"https://www.eater.com/maps/archives/{i + 1}")

            # Parse urls
            guides = []
            a_tags = soup.find_all("a")
            for a_tag in a_tags:
                analytics_link = a_tag.attrs.get('data-analytics-link')
                if analytics_link == "mapstack":
                    url = a_tag.attrs.get("href")
                    guides.append(url)

            for guide in guides:
                # Register new url
                instance, created = JournoPageModel.objects.get_or_create(
                    source_id=EaterStructured.source_name,
                    url=guide
                )

                # Set flow if this process is ran by flow
                if created and flow:
                    instance.flow = flow
                    instance.save()

                # Set ignored if this url is already processed
                true_url_query = JournoPageModel.objects.filter(
                    true_url=guide
                )
                if true_url_query.exists():
                    instance.set_ignored("True url is already processed")

    @staticmethod
    def parse():
        # Get all non-ignored, non-parsed Page
        pages = JournoPageModel.objects.filter(
            source_id=EaterStructured.source_name,
            ignoredAt=None,
            parsedAt=None,
        )

        for page in pages:
            true_url, soup = fetch_with_cache(page.url)
            page.set_true_url(true_url)

            error_message, name = eater_utils.parse_name(soup)
            if error_message:
                page.set_ignored(error_message)
                continue

            page.title = name

            error_message, external_published_at = eater_utils.parse_external_published_at(soup)
            if error_message:
                page.set_ignored(error_message)
                continue
            page.externalPublishedAt = external_published_at

            error_message, description = eater_utils.parse_description(soup)
            if error_message:
                page.set_ignored(error_message)
                continue
            page.description = description

            error_message, external_attribution = eater_utils.parse_external_attribution(soup)
            if error_message:
                page.set_ignored(error_message)
                continue
            page.externalAttribution = external_attribution

            page.media = [
                {
                    "url": soup.find("meta", {"name": "sailthru.image.full"}).attrs.get("content")
                }
            ]

            excerpt_container_tag = soup.find("div", {
                "class": "c-entry-content c-mapstack__content"
            })

            if excerpt_container_tag:
                excerpt_container_tag = excerpt_container_tag.find("p", recursive=False)

                if excerpt_container_tag:
                    page.excerpt = excerpt_container_tag.text

            mapstacks_soup = soup.find("div", {"class": "c-mapstack c-mapstack-improved"})

            if not mapstacks_soup:
                page.set_ignored(
                    "This articles have no mapstacks, no location information can be gathered for this article"
                )
                continue

            mapstacks = mapstacks_soup.attrs.get("data-cdata")
            mapstacks = json.loads(mapstacks)

            mapstacks_data = {}

            for card in mapstacks['cards']:
                if card['type'] == 'point':
                    mapstacks_data[card['slug'].strip()] = {
                        "lat": card['lat'],
                        "lon": card['lon'],
                        "title": card['title'].strip()
                    }

            place_soup = soup.find("main", {"id": "content"})
            place_tags = place_soup.find_all("section", {"class": "c-mapstack__card"})
            for place_tag in place_tags:
                card_slug = place_tag.attrs.get("data-slug").strip()
                if not card_slug or card_slug not in mapstacks_data:
                    continue

                _extraData = {}

                place = JournoPlaceModel()
                place.page = page
                place.externalAttribution = page.externalAttribution
                place.externalPublishedAt = page.externalPublishedAt
                place.urlTitle = page.title
                place.url = page.true_url
                place.name = mapstacks_data[card_slug]['title']
                place.lat = mapstacks_data[card_slug]['lat']
                place.long = mapstacks_data[card_slug]['lon']

                description_tag = place_tag.find("div", {"class": "c-entry-content"})
                place.description = description_tag.text.strip()

                address_tag = place_tag.find("div", {"class": "c-mapstack__address"})
                _extraData['address'] = address_tag.text.strip()

                number_tag = place_tag.find("div", {"class": "c-mapstack__phone"})
                if number_tag:
                    _extraData['phone'] = number_tag.text.strip()

                website_url_tag = place_tag.select_one("a[data-analytics-link='link-icon']")
                if website_url_tag:
                    _extraData['website'] = website_url_tag["href"]

                images = []

                featuredTag = place_tag.find("div", {"class": "c-mapstack__card-featured"})
                if featuredTag:
                    featuredTag.decompose()

                figure_soup = place_tag.find("figure", {"class": "e-image"})
                if not figure_soup:
                    figure_soup = place_tag

                image_tag = figure_soup.find(
                    "span", {"class": "e-image__image"}
                )

                if image_tag:
                    image = {
                        "url": image_tag.attrs.get("data-original"),
                    }
                    cite_tag = figure_soup.find("cite")
                    if cite_tag:
                        image['credit'] = cite_tag.text
                    else:
                        image_credit_tag = place_tag.find("a", {"class": "ql-link"})
                        image['credit'] = image_credit_tag.text if image_credit_tag else 'Eater'
                    images.append(image)

                place.media = images

                place.set_extra(_extraData)

                if JournoPlaceModel.objects.filter(
                        url=place.url,
                        name=place.name,
                        description=place.description
                ).exists():
                    continue
                place.save()

            page.set_parsed()
