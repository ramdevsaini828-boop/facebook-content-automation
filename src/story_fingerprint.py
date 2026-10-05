import re


STOP_WORDS = {
    "the", "and", "for", "with", "from", "that", "this",
    "news", "today", "latest", "report", "reports",
    "breaking", "live", "update", "updates",
    "india", "will", "has", "have", "was", "were",
    "into", "after", "before", "over", "under",
    "says", "said", "according",
}

SPAM_WORDS = {
    "livestream",
    "livestreams",
    "streaming",
    "stream",
    "watch",
    "watchlive",
    "livewatch",
    "broadcast",
    "broadcasting",
    "livescore",
    "live-score",
    "scorecard",
    "highlights",
    "prediction",
    "predictions",
    "commentary",
    "free",
    "online",
}


def normalize_text(text):
    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"[^\w\s\u0900-\u097f-]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def get_clean_words(text):
    text = normalize_text(text)

    words = text.split()

    result = []

    for word in words:

        word = word.strip("-")

        if len(word) < 3:
            continue

        if word in STOP_WORDS:
            continue

        if word in SPAM_WORDS:
            continue

        result.append(word)

    return set(result)


def clean_keywords(keywords):
    """
    Remove spam/noise from existing story keywords.
    """

    cleaned = []

    for keyword in keywords or []:

        words = get_clean_words(keyword)

        if not words:
            continue

        # Don't preserve a keyword if it is purely spam.
        if all(
            word in SPAM_WORDS
            for word in words
        ):
            continue

        value = " ".join(sorted(words))

        if value and value not in cleaned:
            cleaned.append(value)

    return cleaned[:20]


def build_fingerprint(
    topic="",
    keywords=None,
    articles=None,
):
    """
    Build a compact identity for a story.

    The fingerprint deliberately ignores
    livestream/watch/streaming noise.
    """

    words = set()

    words.update(
        get_clean_words(topic)
    )

    for keyword in clean_keywords(
        keywords or []
    ):
        words.update(
            get_clean_words(keyword)
        )

    # Use article headlines as additional context.
    for article in (articles or [])[:30]:

        title = article.get(
            "title",
            ""
        )

        article_words = get_clean_words(
            title
        )

        words.update(
            article_words
        )

    return sorted(words)


def fingerprint_overlap(
    fingerprint_a,
    fingerprint_b,
):
    a = set(fingerprint_a or [])
    b = set(fingerprint_b or [])

    if not a or not b:
        return 0.0

    intersection = a.intersection(b)

    union = a.union(b)

    return len(intersection) / len(union)


def important_overlap(
    fingerprint_a,
    fingerprint_b,
):
    a = set(fingerprint_a or [])
    b = set(fingerprint_b or [])

    if not a or not b:
        return 0

    return len(
        a.intersection(b)
    )
