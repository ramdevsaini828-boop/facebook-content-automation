import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote


GOOGLE_TRENDS_RSS = (
    "https://trends.google.com/trending/rss"
    "?geo=IN&hl=en-US"
)

GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search"
    "?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
)


# --------------------------------------------------
# LOW VALUE TOPICS
# --------------------------------------------------

LOW_VALUE_KEYWORDS = [
    "horoscope",
    "rashifal",
    "राशिफल",
    "astrology",
    "weather",
    "lottery",
    "ज्योतिष",
    "today horoscope",
]


# --------------------------------------------------
# GENERIC TOPICS
# --------------------------------------------------

GENERIC_TOPICS = [
    "आतंकवाद",
    "terrorism",
    "news",
    "latest news",
    "breaking news",
    "today",
    "भारत",
    "india",
    "world",
    "politics",
    "राजनीति",
    "sports",
    "खेल",
    "economy",
    "अर्थव्यवस्था",
]


def get_google_trends(limit=20):
    """
    Google Trends se India ke current trending topics fetch karta hai.
    """

    try:
        response = requests.get(
            GOOGLE_TRENDS_RSS,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        root = ET.fromstring(response.content)

        topics = []

        for item in root.findall(".//item"):

            title = item.findtext("title")

            traffic = item.findtext(
                "{https://trends.google.com/trending/rss}approx_traffic"
            )

            if title:

                topics.append({
                    "topic": title.strip(),
                    "traffic": traffic
                })

            if len(topics) >= limit:
                break

        return topics

    except Exception as error:

        print(
            f"Google Trends error: {error}"
        )

        return []


# --------------------------------------------------
# LOW VALUE CHECK
# --------------------------------------------------

def is_low_value_topic(topic):
    """
    Low-value / unsuitable topics ko filter karta hai.
    """

    topic_lower = topic.lower().strip()

    for keyword in LOW_VALUE_KEYWORDS:

        if keyword.lower() in topic_lower:
            return True

    return False


# --------------------------------------------------
# GENERIC TOPIC CHECK
# --------------------------------------------------

def is_generic_topic(topic):
    """
    Aise keywords ko filter karta hai
    jo akela meaningful news topic nahi batate.
    """

    normalized = topic.lower().strip()

    if normalized in GENERIC_TOPICS:
        return True

    words = normalized.split()

    # Bahut chhota aur unclear keyword
    if len(words) == 1 and len(normalized) < 5:
        return True

    return False


# --------------------------------------------------
# NEWS COVERAGE
# --------------------------------------------------

def check_news_coverage(topic):
    """
    Google News RSS par topic ki recent coverage check karta hai.
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

        articles = root.findall(".//item")

        return len(articles)

    except Exception as error:

        print(
            f"News check error for "
            f"'{topic}': {error}"
        )

        return 0


# --------------------------------------------------
# SCORE
# --------------------------------------------------

def calculate_score(
    position,
    news_count,
    topic
):
    """
    Preliminary topic quality score.
    """

    # Trend position score
    trend_score = max(
        0,
        100 - ((position - 1) * 4)
    )

    # News coverage score
    if news_count >= 20:

        news_score = 30

    elif news_count >= 10:

        news_score = 25

    elif news_count >= 5:

        news_score = 18

    elif news_count >= 2:

        news_score = 10

    else:

        news_score = 0

    # Low value penalty
    penalty = 0

    if is_low_value_topic(topic):

        penalty = 50

    return (
        trend_score
        + news_score
        - penalty
    )


# --------------------------------------------------
# TOP TOPICS
# --------------------------------------------------

def get_top_topics(limit=3):

    """
    Trending topics me se
    strongest topics select karta hai.
    """

    trends = get_google_trends(
        limit=20
    )

    if not trends:

        return []

    scored_topics = []

    print(
        "\n🔎 Checking news coverage...\n"
    )

    for position, item in enumerate(
        trends,
        start=1
    ):

        topic = item["topic"]

        # ------------------------------------------
        # LOW VALUE FILTER
        # ------------------------------------------

        if is_low_value_topic(topic):

            print(
                f"⏭️ Skipping low-value topic: "
                f"{topic}"
            )

            continue

        # ------------------------------------------
        # GENERIC FILTER
        # ------------------------------------------

        if is_generic_topic(topic):

            print(
                f"⏭️ Skipping generic topic: "
                f"{topic}"
            )

            continue

        # ------------------------------------------
        # NEWS CHECK
        # ------------------------------------------

        news_count = check_news_coverage(
            topic
        )

        # ------------------------------------------
        # SCORE
        # ------------------------------------------

        score = calculate_score(
            position,
            news_count,
            topic
        )

        scored_topics.append({

            "topic": topic,

            "traffic": item["traffic"],

            "news_count": news_count,

            "score": score

        })

        print(
            f"{position}. {topic} | "
            f"News: {news_count} | "
            f"Score: {score}"
        )

    # ------------------------------------------
    # SORT
    # ------------------------------------------

    scored_topics.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return scored_topics[:limit]


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "\n🔥 TOP 3 VIRAL TOPICS\n"
    )

    top_topics = get_top_topics(3)

    for number, topic in enumerate(
        top_topics,
        start=1
    ):

        print(
            f"{number}. "
            f"{topic['topic']} "
            f"(Score: {topic['score']})"
        )
