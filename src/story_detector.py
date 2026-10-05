import re
from difflib import SequenceMatcher


STOP_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "news",
    "today",
    "latest",
    "india",
    "report",
    "reports",
    "breaking",
}


def normalize_text(text):
    if not text:
        return ""

    text = text.lower()

    text = re.sub(r"[^\w\s\u0900-\u097f]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_words(text):
    text = normalize_text(text)

    words = text.split()

    return {
        word
        for word in words
        if len(word) > 2 and word not in STOP_WORDS
    }


def similarity(text_a, text_b):
    a = normalize_text(text_a)
    b = normalize_text(text_b)

    if not a or not b:
        return 0.0

    return SequenceMatcher(
        None,
        a,
        b,
    ).ratio()


def keyword_overlap(article_title, story_keywords):
    article_words = get_words(article_title)

    matches = 0

    for keyword in story_keywords:
        keyword_words = get_words(keyword)

        if not keyword_words:
            continue

        if article_words.intersection(keyword_words):
            matches += 1

    return matches


def article_matches_story(article, story):
    title = article.get("title", "")

    if not title:
        return False, 0.0

    story_topic = story.get("topic", "")

    story_keywords = story.get(
        "keywords",
        [],
    )

    # --------------------------------------------
    # Topic similarity
    # --------------------------------------------

    topic_score = similarity(
        title,
        story_topic,
    )

    # --------------------------------------------
    # Keyword matching
    # --------------------------------------------

    overlap = keyword_overlap(
        title,
        story_keywords,
    )

    keyword_score = min(
        overlap / 3,
        1.0,
    )

    # --------------------------------------------
    # Final score
    # --------------------------------------------

    score = (
        topic_score * 0.65
        + keyword_score * 0.35
    )

    return score >= 0.35, score


def find_matching_story(article, stories):
    best_story = None
    best_score = 0.0

    for story in stories:
        if story.get("status") != "active":
            continue

        matched, score = article_matches_story(
            article,
            story,
        )

        if matched and score > best_score:
            best_story = story
            best_score = score

    return best_story, best_score
