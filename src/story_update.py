from story_detector import (
    find_matching_story
) 
from datetime import datetime

from story_detector import find_matching_story


def article_key(article):
    title = (
        article.get("title")
        or ""
    ).strip().lower()

    source = (
        article.get("source")
        or article.get("provider")
        or ""
    ).strip().lower()

    return f"{title}|{source}"


def is_duplicate_article(article, story):
    new_key = article_key(article)

    for old_article in story.get("articles", []):
        if article_key(old_article) == new_key:
            return True

    return False


def classify_development(article, story):
    """
    Decide whether article is:
    - duplicate
    - new development
    """

    if is_duplicate_article(
        article,
        story,
    ):
        return "duplicate"

    return "new"


def add_article_to_story(story, article):
    now = datetime.now().isoformat()

    classification = classify_development(
        article,
        story,
    )

    if classification == "duplicate":
        return {
            "status": "duplicate",
            "story": story,
        }

    title = (
        article.get("title")
        or ""
    ).strip()

    source = (
        article.get("source")
        or article.get("provider")
        or ""
    ).strip()

    # --------------------------------------------
    # Store article
    # --------------------------------------------

    story.setdefault(
        "articles",
        []
    ).append(article)

    # --------------------------------------------
    # Store source
    # --------------------------------------------

    if source:
        sources = story.setdefault(
            "sources",
            []
        )

        if source not in sources:
            sources.append(source)

    # --------------------------------------------
    # Store development
    # --------------------------------------------

    development = {
        "timestamp": now,
        "title": title,
        "source": source,
        "published": article.get(
            "published",
            "",
        ),
        "link": article.get(
            "link",
            "",
        ),
        "type": "new_development",
    }

    story.setdefault(
        "developments",
        []
    ).append(development)

    # --------------------------------------------
    # Timeline
    # --------------------------------------------

    timeline_item = {
        "timestamp": now,
        "title": title,
        "source": source,
        "link": article.get(
            "link",
            "",
        ),
    }

    story.setdefault(
        "timeline",
        []
    ).append(timeline_item)

    story["last_updated"] = now

    return {
        "status": "new",
        "story": story,
        "development": development,
    }


def update_stories_with_articles(
    stories,
    articles,
):
    results = []

    for article in articles:

        story, score = find_matching_story(
            article,
            stories,
        )

        if story is None:
            results.append({
                "status": "unmatched",
                "article": article,
            })

            continue

        result = add_article_to_story(
            story,
            article,
        )

        result["match_score"] = score

        results.append(result)

    return results


def get_new_developments(results):
    developments = []

    for result in results:

        if result.get("status") != "new":
            continue

        development = result.get(
            "development"
        )

        if development:
            developments.append(
                development
            )

    return developments
