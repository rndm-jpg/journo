def parse_name(soup) -> (str, str):
    try:
        name_tag = soup.find("meta", {"name": "sailthru.title"})
        if name_tag:
            return None, name_tag.attrs.get("content")

        if not name_tag:
            name_tag = soup.find("head").find("title")

        if '404' in name_tag.text:
            return "Page returned 404", None

        return None, name_tag.text[
                     : name_tag.text.lower().index("- eater")
                     ].strip()
    except:
        return "Error while parsing name", None


def parse_external_published_at(soup) -> (str, str):
    try:
        external_published_at_soup = soup.find("meta", {"property": "article:modified_time"})
        result = external_published_at_soup.attrs.get("content")

        # IGNORE externalPublishedAt Before 2018
        import dateutil.parser
        publish_date = dateutil.parser.isoparse(result)
        if publish_date.year < 2018:
            return "This articles is published before 2018", None

        return None, result
    except:
        return "Error while parsing externalPublishedAt", None


def parse_description(soup) -> (str, str):
    try:
        description_soup = soup.find("meta", {"name": "description"})
        return None, description_soup.attrs.get("content")
    except:
        return "Error while parsing description", None


def parse_external_attribution(soup) -> (str, str):
    try:
        author_tags = soup.find_all("meta", {"name": "parsely-author"})
        authors = []
        for author_tag in author_tags:
            authors.append(author_tag.attrs.get("content"))

        result = ", ".join(authors)

        if result:
            return None, result

        author_tag = soup.find("meta", {"property": "author"})
        return None, author_tag.attrs.get("content") if author_tag else 'Eater'
    except:
        return "Error while parsing externalAttribution", None
