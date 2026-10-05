import re
from datetime import datetime, timezone


# Words that usually indicate that a headline is
# reporting someone else's statement or an unconfirmed development.
REPORT_WORDS = {
    "report",
    "reports",
    "reported",
    "according",
    "claims",
    "claim",
    "says",
    "said",
    "sources",
    "likely",
    "may",
    "might",
    "could",
    "expected",
    "in talks",
    "talks",
    "rumoured",
    "rumored",
    "allegedly",
}


RELIABLE_SOURCES = {
    "reuters": 10,
    "associated press": 10,
    "the hindu": 9,
    "indian express": 9,
    "the indian express": 9,
    "the times of india": 8,
    "ndtv": 8,
    "india today": 8,
    "hindustan times": 8,
    "moneycontrol.com": 8,
    "moneycontrol": 8,
    "economic times": 8,
    "the economic times": 8,
    "the kathmandu post": 8,
    "kathmandu post": 8,
    "nepalnews.com": 7,
    "the rising nepal": 7,
    "news18": 7,
    "outlook india": 7,
}


def normalize(text):
    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\u0900-\u097f\u0900-\u097f ]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def source_score(source):
    source_normalized = normalize(source)

    for name, score in RELIABLE_SOURCES.items():

        if name in source_normalized:
            return score

    return 4


def contains_report_language(title):
    title_normalized = normalize(title)

    for word in REPORT_WORDS:

        if word in title_normalized:
            return True

    return False


def extract_numbers(text):
    """
    Extract useful numerical information from headlines.
    """

    if not text:
        return []

    patterns = [
        r"₹\s?[\d,.]+\s?(?:crore|lakh|million|billion)?",
        r"\b\d+(?:\.\d+)?\s?%",
        r"\b\d+(?:\.\d+)?\s?(?:crore|lakh|million|billion)\b",
        r"\b\d+(?:st|nd|rd|th)\b",
        r"\b\d{1,4}\s?(?:days|years|months|hours)\b",
        r"\b\d{4}\b",
    ]

    results = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        results.extend(matches)

    # Remove duplicates while preserving order
    unique = []

    for item in results:

        item = item.strip()

        if item not in unique:
            unique.append(item)

    return unique


def classify_article(article):
    """
    Initial evidence classification.

    IMPORTANT:
    This does not claim that a statement is independently verified.
    It classifies the nature of the headline.
    """

    title = article.get("title", "")
    source = article.get("source", "")

    if contains_report_language(title):

        evidence_type = "CLAIM/REPORT"

    else:

        evidence_type = "REPORTED_FACT"

    score = source_score(source)

    if score >= 9:
        confidence = "HIGH"
    elif score >= 7:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "title": title,
        "source": source,
        "published": article.get("published"),
        "link": article.get("link"),
        "provider": article.get("provider"),
        "evidence_type": evidence_type,
        "confidence": confidence,
        "source_score": score,
        "numbers": extract_numbers(title),
    }


def build_evidence_dataset(topic, event, articles):

    evidence = []

    for article in articles:

        item = classify_article(article)

        evidence.append(item)

    # Highest-quality sources first
    evidence.sort(
        key=lambda x: (
            x["source_score"],
            x["confidence"],
        ),
        reverse=True
    )

    return {
        "topic": topic,
        "event_score": event.get("score"),
        "event_keywords": event.get(
            "keywords",
            []
        ),
        "evidence_count": len(evidence),
        "evidence": evidence,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def print_evidence_dataset(dataset):

    print("\n" + "=" * 60)
    print(" 🧾 EVIDENCE DATASET")
    print("=" * 60)

    print(
        f"Topic: {dataset['topic']}"
    )

    print(
        f"Evidence items: "
        f"{dataset['evidence_count']}"
    )

    for index, item in enumerate(
        dataset["evidence"],
        start=1
    ):

        print("\n" + "-" * 60)

        print(
            f"{index}. {item['title']}"
        )

        print(
            f"   Type: "
            f"{item['evidence_type']}"
        )

        print(
            f"   Confidence: "
            f"{item['confidence']}"
        )

        print(
            f"   Source: "
            f"{item['source']}"
        )

        print(
            f"   Published: "
            f"{item['published']}"
        )

        if item["numbers"]:

            print(
                "   Numbers: "
                + ", ".join(
                    item["numbers"]
                )
            )

        print(
            f"   URL: "
            f"{item['link']}"
        )
