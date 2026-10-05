from story_fingerprint import (
    build_fingerprint,
    clean_keywords,
) 
import json
import os
from datetime import datetime


STORIES_FILE = "data/active_stories.json"
ARTICLES_FILE = "data/processed_articles.json"


def ensure_data_directory():
    os.makedirs("data", exist_ok=True)


def load_json(filename, default):
    ensure_data_directory()

    if not os.path.exists(filename):
        return default

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(filename, data):
    ensure_data_directory()

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def load_active_stories():
    return load_json(STORIES_FILE, [])


def save_active_stories(stories):
    save_json(STORIES_FILE, stories)


def load_processed_articles():
    return load_json(ARTICLES_FILE, [])


def save_processed_articles(articles):
    save_json(ARTICLES_FILE, articles)


def create_story(topic, event):

    now = datetime.now().isoformat()

    raw_keywords = event.get(
        "keywords",
        []
    )

    keywords = clean_keywords(
        raw_keywords
    )

    story_id = build_story_id(
        topic,
        keywords
    )

    fingerprint = build_fingerprint(
        topic=topic,
        keywords=keywords,
        articles=event.get(
            "articles",
            []
        ),
    )

    return {
        "story_id": story_id,
        "topic": topic,
        "status": "active",

        "first_seen": now,
        "last_updated": now,

        "keywords": keywords[:15],

        "fingerprint": fingerprint,

        "articles": [],
        "developments": [],
        "sources": [],
        "timeline": [],
    }


def build_story_id(topic, keywords):
    import re

    text = topic

    if keywords:
        text += "_" + "_".join(keywords[:3])

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\u0900-\u097f]+",
        "_",
        text,
    )

    text = text.strip("_")

    if not text:
        text = "unknown_story"

    return text[:120]
