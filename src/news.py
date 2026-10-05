import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from email.utils import parsedate_to_datetime


GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search"
    "?q={query}"
    "&hl=en-IN"
    "&gl=IN"
    "&ceid=IN:en"
)


def get_news_articles(topic, limit=10):
    """
    Kisi trending topic ke recent Google News articles
    fetch karta hai.
    """

    try:
        encoded_topic = quote(topic)

        url = GOOGLE_NEWS_RSS.format(
            query=encoded_topic
        )

        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.content
        )

        articles = []

        for item in root.findall(".//item"):

            title = item.findtext("title")
            link = item.findtext("link")
            pub_date = item.findtext("pubDate")
            source_element = item.find("source")

            source = None

            if source_element is not None:
                source = source_element.text

            # Date ko readable format me convert karna
            published = pub_date

            if pub_date:

                try:

                    date_object = parsedate_to_datetime(
                        pub_date
                    )

                    published = date_object.strftime(
                        "%Y-%m-%d %H:%M"
                    )

                except Exception:
                    pass

            if title:

                articles.append({

                    "title": title.strip(),

                    "source": (
                        source.strip()
                        if source
                        else "Unknown"
                    ),

                    "published": published,

                    "link": link

                })

            if len(articles) >= limit:
                break

        return articles

    except Exception as error:

        print(
            f"News fetch error for "
            f"'{topic}': {error}"
        )

        return []


def print_news_articles(
    topic,
    limit=10
):

    print(
        f"\n📰 NEWS FOR: {topic}\n"
    )

    articles = get_news_articles(
        topic,
        limit
    )

    if not articles:

        print(
            "No news articles found."
        )

        return

    for number, article in enumerate(
        articles,
        start=1
    ):

        print(
            f"\n{number}. "
            f"{article['title']}"
        )

        print(
            f"   Source: "
            f"{article['source']}"
        )

        print(
            f"   Published: "
            f"{article['published']}"
        )

        print(
            f"   Link: "
            f"{article['link']}"
        )


if __name__ == "__main__":

    # Test
    test_topic = "भगवंत मान"

    print_news_articles(
        test_topic,
        limit=10
    )
