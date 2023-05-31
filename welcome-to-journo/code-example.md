# Expanding Journo's capability in minutes

## Meant to be Extended

Seamlessly extend Journo's functionality by creating custom 'extension' sources. This page serves as your guide, to expand Journo's capabilities according to your specific needs. Discover the step-by-step process to create and integrate your own extensions for enhanced data extraction and processing.

## Creating your Model

To create your own model, follow the following steps:
1. Create a folder with a unique name for your source within the 'src' folder. For instance, use the path /src/mysource.py.
2. Your model should extend the 'GenericSource' model as the superclass.&#x20;

By following this structure, you can customize and integrate your source into Journo.

Example code:

<pre class="language-python" data-title="src/eater__structured.py"><code class="lang-python"><strong>class EaterStructured(GenericSource):
</strong>    source_name = "EATER__STRUCTURED"
</code></pre>

## Creating the 'Crawling' Function

The crawling function, true to its name, enables Journo to navigate through web pages. Its purpose is to create a 'JournoPageModel' instance, ensuring that the URL is included at a minimum. With this function, Journo traverses websites, gathering crucial data to drive your location information workflow.&#x20;

`src/eater__structured.py`
```python
...
    @staticmethod
    def crawl():
        # Loop from page 1 to page 10
        limit = 100
        for i in range(0, limit):
            # Fetch
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
                JournoPageModel.objects.create(
                    source_id=EaterStructured.source_name,
                    url=guide
                )
...
```

## Creating the 'Parsing' Function

The parsing function plays a crucial role in Journo's workflow by processing the links of created JournoPageModels. It fetches and parses the HTML content, extracting essential information. The primary objective of this function is to enrich the JournoPageModel by populating its remaining attributes.&#x20;

By fetching and parsing HTML, the parsing function enhances the completeness of the JournoPageModel, ensuring a comprehensive set of data for further analysis.

```python
...
@staticmethod
def parse():
    # Get all non-ignored, non-parsed Page
    pages = JournoPageModel.objects.filter(
        source_id=EaterStructured.source_name,
        ignoredAt=None,
        parsedAt=None,
    )

    for page in pages:
        soup = fetch_with_cache(page.url)
        
        ...
        # filling JournoPageModel's attributes
        page.title = name
        page.externalPublishedAt = external_published_at
        page.description = eater_utils.parse_description(soup)
        page.save()
        ...
        
        # Creating JournoPlaceModels
        for place_tag in place_tags:
            ...
            place = JournoPlaceModel()
            place.page = page
            place.lat = mapstacks_data[card_slug]['lat']
            place.long = mapstacks_data[card_slug]['lon']
            place.save()
            ...

        page.set_parsed()
...
```

## Registering your Source to Database and to Function Mapper

To enable Journo to utilize your function, you need to register your source\_id in the database and function mapper. You can insert your source\_id into the database using Django with the following code:

```python
SourceModel.objects.create(name="eater")
```

By executing this code, you can register your source\_id in the Journo database, allowing seamless integration with the platform. Empower Journo with your unique source and unlock the full potential of data extraction and processing.

To update the `do_crawl` and `do_parse` functions in `/journo__globals/function_mapper.py`, follow these example:

`function_mapper.py`
```python
def do_crawl(source: str, flow=None):
    ...
    if source == 'EATER__STRUCTURED':
        EaterStructured.crawl(flow)
    ...

def do_parse(source: str):
    ...
    if source == 'EATER__STRUCTURED':
        EaterStructured.parse()
    ...
```

By updating the `do_crawl` and `do_parse` functions in the `function_mapper.py` file, you ensure that Journo can properly utilize your specific crawling and parsing functions for your registered source. This allows for seamless integration and efficient data extraction from your source.

Congratulations! With your source\_id successfully registered and integrated into Journo's functionality, you can now utilize it to perform API calls in the crawl, parse, match, and upload processes.&#x20;

Leverage the power of your custom source\_id to seamlessly access and process data, enabling Journo to extract valuable insights from your source. Enjoy the enhanced capabilities and possibilities that come with integrating your source\_id into Journo's workflow.
