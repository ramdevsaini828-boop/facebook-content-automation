from collections import Counter
from datetime import datetime, timezone


# Higher score = generally stronger/more reliable source
SOURCE_RELIABILITY = {
    "reuters": 10,
    "associated press": 10,
    "the hindu": 9,
    "indian express": 9,
    "times of india": 8,
    "ndtv": 8,
    "india today": 8,
    "hindustan times": 8,
    "moneycontrol": 8,
    "news18": 7,
    "outlook india": 7,
    "mid-day": 7,
    "economic times": 8,
    "kathmandu post": 8,
    "nepalnews": 7,
    "rising nepal": 7,
    "daily excelsior": 6,
    "devdiscourse": 5,
    "pinkvilla": 5,
    "bollywood hungama": 5,
    "movietalkies": 4,
}


STOP_WORDS = {
    "the", "and", "for", "with", "from", "after", "before",
    "this", "that", "have", "has", "had", "will", "into",
    "over", "under", "their", "they", "them", "been",
    "were", "are", "was", "is", "to", "of", "in", "on",
    "at", "by", "a", "an", "as", "or", "but", "new",
    "latest", "report", "reports", "says", "said",
    "what", "know", "here", "today"
}


def normalize_text(text):
    if not text:
        return ""

    text = text.lower()

    for char in ",.!?:;|()[]{}'\"/-":
        text = text.replace(char, " ")

    return " ".join(text.split())


def get_source_score(source):
    source_normalized = normalize_text(source)

    for source_name, score in SOURCE_RELIABILITY.items():
        if source_name in source_normalized:
            return score

    return 4


def get_keywords(title):
    words = normalize_text(title).split()

    return {
        word
        for word in words
        if len(word) >= 4 and word not in STOP_WORDS
    }


def freshness_score(article):
    published = article.get("published_datetime")

    if not published:
        return 0

    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)

    age_hours = (
        now - published
    ).total_seconds() / 3600

    if age_hours <= 6:
        return 30

    if age_hours <= 12:
        return 25

    if age_hours <= 24:
        return 20

    if age_hours <= 36:
        return 15

    if age_hours <= 48:
        return 10

    return 0


def build_event_candidates(articles):
    """
    Groups articles using overlapping important keywords.
    This is a lightweight, free event-clustering approach.
    """

    if not articles:
        return []

    article_data = []

    for article in articles:
        keywords = get_keywords(article.get("title", ""))

        article_data.append({
            "article": article,
            "keywords": keywords,
        })

    clusters = []

    for item in article_data:

        best_cluster = None
        best_overlap = 0

        for cluster in clusters:

            overlap = len(
                item["keywords"] &
                cluster["keywords"]
            )

            if overlap > best_overlap:
                best_overlap = overlap
                best_cluster = cluster

        if best_cluster is not None and best_overlap >= 2:

            best_cluster["articles"].append(
                item["article"]
            )

            best_cluster["keywords"].update(
                item["keywords"]
            )

        else:

            clusters.append({
                "articles": [item["article"]],
                "keywords": set(item["keywords"]),
            })

    return clusters


def score_cluster(cluster):

    articles = cluster["articles"]

    if not articles:
        return 0

    # Independent sources
    sources = {
        normalize_text(
            article.get("source", "")
        )
        for article in articles
        if article.get("source")
    }

    source_diversity = len(sources)

    # Freshness
    freshness = sum(
        freshness_score(article)
        for article in articles
    )

    # Reliability
    reliability = sum(
        get_source_score(
            article.get("source", "")
        )
        for article in articles
    )

    # Duplicate protection
    unique_titles = {
        normalize_text(
            article.get("title", "")
        )
        for article in articles
    }

    duplicate_penalty = max(
        0,
        len(articles) - len(unique_titles)
    ) * 3

    score = (
        len(articles) * 5
        + source_diversity * 8
        + freshness
        + reliability
        - duplicate_penalty
    )

    return score


def rank_events(articles):

    clusters = build_event_candidates(articles)

    ranked = []

    for cluster in clusters:

        score = score_cluster(cluster)

        ranked.append({
            "score": score,
            "articles": cluster["articles"],
            "keywords": sorted(
                cluster["keywords"],
                key=len,
                reverse=True
            )[:15],
        })

    ranked.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked


def print_ranked_events(events):

    print("\n" + "=" * 60)
    print("🔥 RANKED EVENTS")
    print("=" * 60)

    if not events:
        print("❌ No event candidates found.")
        return

    for number, event in enumerate(
        events[:5],
        start=1
    ):

        print(
            f"\nEVENT {number}"
        )

        print(
            f"Score: {event['score']}"
        )

        print(
            "Keywords: "
            + ", ".join(
                event["keywords"][:8]
            )
        )

        print(
            f"Articles: "
            f"{len(event['articles'])}"
        )

        sources = sorted({
            article.get(
                "source",
                "Unknown"
            )
            for article in event["articles"]
        })

        print(
            "Sources: "
            + ", ".join(sources[:8])
        )

        print("Headlines:")

        for article in event["articles"][:5]:
            print(
                f"  - {article['title']}"
            )
