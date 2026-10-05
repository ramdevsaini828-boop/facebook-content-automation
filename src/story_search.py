import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote


GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search?"
    "q={query}&hl=en-IN&gl=IN&ceid=IN:en"
)


def fetch_story_news(query, limit=20):
    """
    Search Google News RSS for new articles related to a story.
    """

    url = GOOGLE_NEWS_RSS.format(
        query=quote(query)
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/120 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.content
        )

    except Exception as error:
        print(
            f"⚠️ Story search failed: {error}"
        )
        return []

    articles = []

    for item in root.findall(".//item"):

        title = item.findtext(
            "title",
            default="",
        ).strip()

        link = item.findtext(
            "link",
            default="",
        ).strip()

        published = item.findtext(
            "pubDate",
            default="",
        ).strip()

        source_node = item.find(
            "source"
        )

        source = ""

        if source_node is not None:
            source = (
                source_node.text or ""
            ).strip()

        if not title:
            continue

        articles.append({
            "title": title,
            "source": source,
            "published": published,
            "link": link,
            "provider": "Google News",
        })

        if len(articles) >= limit:
            break

    return articles


def build_story_queries(story):
    """
    Create several searches instead of relying on
    one exact topic phrase.
    """

    topic = story.get(
        "topic",
        "",
    ).strip()

    keywords = [
        keyword.strip()
        for keyword in story.get(
            "keywords",
            [],
        )
        if keyword.strip()
    ]

    queries = []

    if topic:
        queries.append(topic)

    if topic and keywords:
        queries.append(
            f"{topic} {keywords[0]}"
        )

    if topic and len(keywords) >= 2:
        queries.append(
            f"{topic} {keywords[0]} {keywords[1]}"
        )

    # Search specifically for developments
    if topic:
        queries.append(
            f"{topic} latest update"
        )

        queries.append(
            f"{topic} latest development"
        )

    # Remove duplicates
    result = []

    seen = set()

    for query in queries:

        key = query.lower().strip()

        if key in seen:
            continue

        seen.add(key)
        result.append(query)

    return result


def search_active_story(story):
    """
    Search all query variations for one active story.
    """

    queries = build_story_queries(
        story
    )

    all_articles = []

    seen = set()

    for query in queries:

        print(
            f"🔎 Story search: {query}"
        )

        articles = fetch_story_news(
            query,
            limit=20,
        )

        for article in articles:

            key = (
                article.get(
                    "title",
                    "",
                ).lower().strip()
            )

            if not key:
                continue

            if key in seen:
                continue

            seen.add(key)

            all_articles.append(
                article
            )

    return all_articles
