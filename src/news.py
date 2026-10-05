import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search"
    "?q={query}"
    "&hl=en-IN"
    "&gl=IN"
    "&ceid=IN:en"
)


def get_news_articles(topic, limit=15):
    try:
        encoded_topic = quote(topic)
        url = GOOGLE_NEWS_RSS.format(query=encoded_topic)

        response = requests.get(
            url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        response.raise_for_status()

        root = ET.fromstring(response.content)

        articles = []

        for item in root.findall(".//item"):
            title = item.findtext("title")
            link = item.findtext("link")
            pub_date = item.findtext("pubDate")

            source_element = item.find("source")
            source = (
                source_element.text
                if source_element is not None
                else "Unknown"
            )

            published_datetime = None

            if pub_date:
                try:
                    published_datetime = parsedate_to_datetime(pub_date)
                except Exception:
                    pass

            if title:
                articles.append({
                    "title": title.strip(),
                    "source": source.strip() if source else "Unknown",
                    "published": (
                        published_datetime.strftime("%Y-%m-%d %H:%M")
                        if published_datetime
                        else pub_date
                    ),
                    "published_datetime": published_datetime,
                    "link": link
                })

            if len(articles) >= limit:
                break

        return articles

    except Exception as error:
        print(f"News fetch error for '{topic}': {error}")
        return []


def get_fresh_articles(topic, hours=48, limit=15):
    """
    केवल हाल की news निकालता है।
    Default: पिछले 48 घंटे।
    """

    articles = get_news_articles(topic, limit=30)

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours)

    fresh_articles = []

    for article in articles:
        published = article.get("published_datetime")

        if not published:
            continue

        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)

        if published >= cutoff:
            fresh_articles.append(article)

    return fresh_articles[:limit]


def normalize_title(title):
    """
    Headlines को comparison के लिए simple form में बदलता है।
    """

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
        title = title.replace(word, "")

    return " ".join(title.split()).strip()


def find_event_signal(articles):
    """
    Multiple headlines देखकर common event का basic signal निकालता है।
    """

    if not articles:
        return None

    titles = [
        normalize_title(article["title"])
        for article in articles
    ]

    # सबसे common important words
    stop_words = {
        "the", "and", "to", "of", "in", "for",
        "a", "an", "is", "on", "with", "after",
        "from", "as", "at", "by", "new", "will",
        "has", "have", "are", "this"
    }

    word_count = {}

    for title in titles:
        words = set(title.split())

        for word in words:
            if len(word) < 4:
                continue

            if word in stop_words:
                continue

            word_count[word] = word_count.get(word, 0) + 1

    important_words = sorted(
        word_count.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return important_words[:10]


def analyze_topic(topic):
    print(f"\n{'=' * 60}")
    print(f"🔎 ANALYZING: {topic}")
    print(f"{'=' * 60}")

    articles = get_fresh_articles(
        topic,
        hours=48,
        limit=15
    )

    print(f"\n📰 Fresh articles found: {len(articles)}")

    if not articles:
        print("⚠️ No sufficiently fresh articles.")
        return {
            "topic": topic,
            "articles": [],
            "event_signal": []
        }

    for number, article in enumerate(articles, start=1):
        print(f"\n{number}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Published: {article['published']}")

    signal = find_event_signal(articles)

    print("\n🔥 COMMON EVENT SIGNAL:")

    for word, count in signal:
        print(f"   {word} → {count} articles")

    return {
        "topic": topic,
        "articles": articles,
        "event_signal": signal
    }


if __name__ == "__main__":
    analyze_topic("sanjay leela bhansali")
