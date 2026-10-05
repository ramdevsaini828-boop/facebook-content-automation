from difflib import SequenceMatcher

from story_fingerprint import (
    build_fingerprint,
    clean_keywords,
    fingerprint_overlap,
    important_overlap,
)


def normalize_text(text):
    if not text:
        return ""

    return " ".join(
        text.lower().split()
    )


def similarity(text_a, text_b):

    a = normalize_text(text_a)
    b = normalize_text(text_b)

    if not a or not b:
        return 0.0

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()


def article_matches_story(
    article,
    story,
):
    title = article.get(
        "title",
        ""
    )

    if not title:
        return False, 0.0, "unrelated"

    story_topic = story.get(
        "topic",
        ""
    )

    story_keywords = story.get(
        "keywords",
        []
    )

    story_fingerprint = story.get(
        "fingerprint",
        []
    )

    # If old story has no fingerprint,
    # create one dynamically.
    if not story_fingerprint:

        story_fingerprint = build_fingerprint(
            topic=story_topic,
            keywords=story_keywords,
            articles=story.get(
                "articles",
                []
            ),
        )

    article_fingerprint = build_fingerprint(
        topic="",
        keywords=[],
        articles=[
            {
                "title": title
            }
        ],
    )

    overlap = fingerprint_overlap(
        article_fingerprint,
        story_fingerprint,
    )

    important = important_overlap(
        article_fingerprint,
        story_fingerprint,
    )

    title_similarity = similarity(
        title,
        story_topic
    )

    # ------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------

    # Strong direct topic match
    if title_similarity >= 0.65:
        return True, 0.90, "update"

    # Multiple important story terms
    if important >= 3 and overlap >= 0.18:
        return True, 0.80, "update"

    # Two important matching terms
    if important >= 2 and overlap >= 0.12:
        return True, 0.65, "related"

    # Weak match
    if important >= 1 and overlap >= 0.08:
        return True, 0.45, "review"

    return False, overlap, "unrelated"


def find_matching_story(
    article,
    stories,
):

    best_story = None
    best_score = 0.0
    best_type = "unrelated"

    for story in stories:

        if story.get(
            "status"
        ) != "active":
            continue

        matched, score, match_type = (
            article_matches_story(
                article,
                story
            )
        )

        if matched and score > best_score:

            best_story = story
            best_score = score
            best_type = match_type

    return (
        best_story,
        best_score,
        best_type,
    )
