import re
import requests
from datetime import datetime, timezone
from urllib.parse import quote


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; FacebookContentAutomation/1.0)"
}


def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def google_news_search(query, limit=20):
    """
    Google News RSS search.
    Free - no API key required.
    """

    url = (
        "https://news.google.com/rss/search"
        f"?q={quote(query)}"
        "&hl=en-IN"
        "&gl=IN"
        "&ceid=IN:en"
    )

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        import xml.etree.ElementTree as ET

        root = ET.fromstring(response.content)

        articles = []

        for item in root.findall(".//item")[:limit]:

            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")
            source = item.findtext("source", "")

            articles.append({
                "title": clean_text(title),
                "link": link,
                "published": pub_date,
                "source": clean_text(source),
            })

        return articles

    except Exception as e:
        print(f"⚠️ Research search failed: {e}")
        return []


def build_research_queries(topic, event):
    """
    Generate several search queries around the selected event.
    """

    keywords = event.get("keywords", [])

    queries = [
        topic,
    ]

    if keywords:
        queries.append(
            f"{topic} {' '.join(keywords[:3])}"
        )

    # Specific event keywords
    for keyword in keywords[:3]:
        queries.append(
            f"{topic} {keyword}"
        )

    # Remove duplicates
    final_queries = []

    for query in queries:
        query = clean_text(query)

        if query and query not in final_queries:
            final_queries.append(query)

    return final_queries[:5]


def collect_research(topic, event):
    """
    Collect multiple independent news results
    for the selected event.
    """

    print("\n" + "=" * 50)
    print("🔬 DEEP RESEARCH")
    print("=" * 50)

    print(f"Topic: {topic}")

    keywords = event.get("keywords", [])

    print(
        "Event keywords:",
        ", ".join(keywords[:10])
    )

    queries = build_research_queries(topic, event)

    print("\n🔎 Research queries:")

    for query in queries:
        print(f"   • {query}")

    all_articles = []

    for query in queries:

        print(f"\n📰 Searching: {query}")

        articles = google_news_search(
            query,
            limit=15
        )

        print(
            f"   Found: {len(articles)} articles"
        )

        all_articles.extend(articles)

    # Deduplicate by normalized title
    unique = {}

    for article in all_articles:

        title = article["title"].lower()

        title = re.sub(
            r"[^a-z0-9\u0900-\u097f ]",
            " ",
            title
        )

        title = re.sub(
            r"\s+",
            " ",
            title
        ).strip()

        if title and title not in unique:
            unique[title] = article

    articles = list(unique.values())

    print(
        f"\n✅ Unique research articles: {len(articles)}"
    )

    return articles


def print_research_articles(articles):

    print("\n" + "=" * 50)
    print("📚 RESEARCH SOURCES")
    print("=" * 50)

    for index, article in enumerate(
        articles,
        start=1
    ):

        print(f"\n{index}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Date: {article['published']}")
        print(f"   URL: {article['link']}")


def analyze_research(topic, event, articles):

    sources = set()

    for article in articles:

        source = article.get(
            "source",
            ""
        ).strip()

        if source:
            sources.add(source)

    result = {
        "topic": topic,
        "event": event,
        "article_count": len(articles),
        "source_count": len(sources),
        "sources": sorted(sources),
        "articles": articles,
        "researched_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    return result
