import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta
import time


GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search"
    "?q={query}"
    "&hl=en-IN"
    "&gl=IN"
    "&ceid=IN:en"
)

GDELT_API = (
    "https://api.gdeltproject.org/api/v2/doc/doc"
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    ),
    "Accept": (
        "application/rss+xml,"
        "application/xml,"
        "text/xml,"
        "*/*"
    ),
}


# ---------------------------------------------------------
# GOOGLE NEWS
# ---------------------------------------------------------

def get_google_news_articles(topic, limit=15):

    encoded_topic = quote(topic)

    url = GOOGLE_NEWS_RSS.format(
        query=encoded_topic
    )

    for attempt in range(3):

        try:

            response = requests.get(
                url,
                timeout=20,
                headers=HEADERS
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

                source_element = item.find(
                    "source"
                )

                source = (
                    source_element.text
                    if source_element is not None
                    else "Unknown"
                )

                published_datetime = None

                if pub_date:

                    try:
                        published_datetime = (
                            parsedate_to_datetime(
                                pub_date
                            )
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
                        "published": (
                            published_datetime.strftime(
                                "%Y-%m-%d %H:%M"
                            )
                            if published_datetime
                            else pub_date
                        ),
                        "published_datetime":
                            published_datetime,
                        "link": link,
                        "provider": "Google News",
                    })

                if len(articles) >= limit:
                    break

            return articles

        except Exception as error:

            print(
                f"Google News attempt "
                f"{attempt + 1}/3 failed "
                f"for '{topic}': {error}"
            )

            if attempt < 2:
                time.sleep(
                    2 ** attempt
                )

    return []


# ---------------------------------------------------------
# GDELT FALLBACK
# ---------------------------------------------------------

def get_gdelt_articles(topic, limit=15):

    try:

        encoded_topic = quote(
            f'"{topic}"'
        )

        params = {
            "query": encoded_topic,
            "mode": "artlist",
            "maxrecords": limit,
            "timespan": "3d",
            "sort": "datedesc",
            "format": "json",
        }

        response = requests.get(
            GDELT_API,
            params=params,
            timeout=30,
            headers=HEADERS
        )

        response.raise_for_status()

        data = response.json()

        articles = []

        for item in data.get(
            "articles",
            []
        ):

            title = item.get(
                "title"
            )

            url = item.get(
                "url"
            )

            domain = item.get(
                "domain"
            )

            seen_date = item.get(
                "seendate"
            )

            published_datetime = None

            if seen_date:

                try:

                    published_datetime = (
                        datetime.strptime(
                            seen_date,
                            "%Y%m%dT%H%M%SZ"
                        ).replace(
                            tzinfo=timezone.utc
                        )
                    )

                except Exception:
                    pass

            if title:

                articles.append({
                    "title": title.strip(),
                    "source": (
                        domain
                        if domain
                        else "Unknown"
                    ),
                    "published": (
                        published_datetime.strftime(
                            "%Y-%m-%d %H:%M"
                        )
                        if published_datetime
                        else seen_date
                    ),
                    "published_datetime":
                        published_datetime,
                    "link": url,
                    "provider": "GDELT",
                })

        return articles

    except Exception as error:

        print(
            f"GDELT error for "
            f"'{topic}': {error}"
        )

        return []


# ---------------------------------------------------------
# COMBINED NEWS SEARCH
# ---------------------------------------------------------

def get_news_articles(
    topic,
    limit=15
):

    print(
        f"\n📰 Searching news for: "
        f"{topic}"
    )

    google_articles = (
        get_google_news_articles(
            topic,
            limit
        )
    )

    if google_articles:

        print(
            f"✅ Google News returned "
            f"{len(google_articles)} articles"
        )

        return google_articles

    print(
        "⚠️ Google News unavailable."
    )

    print(
        "🔄 Switching to GDELT..."
    )

    gdelt_articles = (
        get_gdelt_articles(
            topic,
            limit
        )
    )

    if gdelt_articles:

        print(
            f"✅ GDELT returned "
            f"{len(gdelt_articles)} articles"
        )

    else:

        print(
            "❌ No articles found "
            "from either source."
        )

    return gdelt_articles


# ---------------------------------------------------------
# FRESHNESS FILTER
# ---------------------------------------------------------

def get_fresh_articles(
    topic,
    hours=48,
    limit=15
):

    articles = get_news_articles(
        topic,
        limit=30
    )

    now = datetime.now(
        timezone.utc
    )

    cutoff = (
        now -
        timedelta(hours=hours)
    )

    fresh_articles = []

    for article in articles:

        published = article.get(
            "published_datetime"
        )

        if not published:
            continue

        if published.tzinfo is None:

            published = published.replace(
                tzinfo=timezone.utc
            )

        if published >= cutoff:

            fresh_articles.append(
                article
            )

    return fresh_articles[:limit]


# ---------------------------------------------------------
# TITLE NORMALIZATION
# ---------------------------------------------------------

def normalize_title(title):

    title = title.lower()

    remove_words = [
        "report",
        "reports",
        "breaking",
        "latest",
        "exclusive",
        "here's what we know",
        "heres what we know",
    ]

    for word in remove_words:

        title = title.replace(
            word,
            ""
        )

    return " ".join(
        title.split()
    ).strip()


# ---------------------------------------------------------
# EVENT SIGNAL
# ---------------------------------------------------------

def find_event_signal(
    articles
):

    if not articles:
        return None

    titles = [
        normalize_title(
            article["title"]
        )
        for article in articles
    ]

    stop_words = {
        "the",
        "and",
        "to",
        "of",
        "in",
        "for",
        "a",
        "an",
        "is",
        "on",
        "with",
        "after",
        "from",
        "as",
        "at",
        "by",
        "new",
        "will",
        "has",
        "have",
        "are",
        "this",
        "that",
        "said",
        "says",
    }

    word_count = {}

    for title in titles:

        words = set(
            title.split()
        )

        for word in words:

            if len(word) < 4:
                continue

            if word in stop_words:
                continue

            word_count[word] = (
                word_count.get(
                    word,
                    0
                ) + 1
            )

    important_words = sorted(
        word_count.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return important_words[:10]


# ---------------------------------------------------------
# TOPIC ANALYSIS
# ---------------------------------------------------------

def analyze_topic(topic):

    print("\n" + "=" * 60)
    print(
        f"🔎 ANALYZING: {topic}"
    )
    print("=" * 60)

    articles = get_fresh_articles(
        topic,
        hours=48,
        limit=15
    )

    print(
        f"\n📰 Fresh articles found: "
        f"{len(articles)}"
    )

    if not articles:

        print(
            "⚠️ No sufficiently fresh "
            "articles."
        )

        return {
            "topic": topic,
            "articles": [],
            "event_signal": []
        }

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
            f"   Provider: "
            f"{article.get('provider', 'Unknown')}"
        )

    signal = find_event_signal(
        articles
    )

    print(
        "\n🔥 COMMON EVENT SIGNAL:"
    )

    for word, count in signal:

        print(
            f"   {word} → {count} articles"
        )

    return {
        "topic": topic,
        "articles": articles,
        "event_signal": signal
    }


if __name__ == "__main__":

    analyze_topic(
        "sanjay leela bhansali"
    )
