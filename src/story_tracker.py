from datetime import datetime

from story_store import (
    load_active_stories,
    save_active_stories,
    create_story,
)

from story_update import (
    update_stories_with_articles,
    get_new_developments,
)

from story_detector import (
    find_matching_story,
)

from story_search import search_active_story

def find_or_create_story(
    topic,
    event,
):
    stories = load_active_stories()

    # Existing story खोजें
    dummy_article = {
        "title": topic,
    }

    story, score = find_matching_story(
        dummy_article,
        stories,
    )

    if story:
        return stories, story, False

    # नई story
    story = create_story(
        topic,
        event,
    )

    stories.append(story)

    save_active_stories(
        stories
    )

    return stories, story, True


def register_initial_articles(
    story,
    articles,
):
    """
    Initial research को story में register करता है।
    """

    existing_titles = {
        (
            article.get("title", "")
            .strip()
            .lower()
        )
        for article in story.get(
            "articles",
            [],
        )
    }

    for article in articles:

        title = (
            article.get("title", "")
            .strip()
            .lower()
        )

        if not title:
            continue

        if title in existing_titles:
            continue

        story.setdefault(
            "articles",
            []
        ).append(article)

        source = (
            article.get("source")
            or article.get("provider")
            or ""
        ).strip()

        if source:
            sources = story.setdefault(
                "sources",
                []
            )

            if source not in sources:
                sources.append(source)

        existing_titles.add(title)

    story["last_updated"] = (
        datetime.now().isoformat()
    )


def track_story(
    topic,
    event,
    new_articles,
):
    """
    Main story tracking function.
    """

    stories, story, created = (
        find_or_create_story(
            topic,
            event,
        )
    )

    if created:

        register_initial_articles(
            story,
            new_articles,
        )

        save_active_stories(
            stories
        )

        return {
            "story": story,
            "created": True,
            "new_developments": [],
            "results": [],
        }

    # Existing story
    results = update_stories_with_articles(
        stories,
        new_articles,
    )

    new_developments = (
        get_new_developments(
            results
        )
    )

    save_active_stories(
        stories
    )

    return {
        "story": story,
        "created": False,
        "new_developments": new_developments,
        "results": results,
    }

def get_new_developments(results):

    developments = []

    for result in results:

        if result.get(
            "status"
        ) != "new":
            continue

        development = result.get(
            "development"
        )

        if development:
            developments.append(
                development
            )

    return developments

def print_story_status(
    tracking_result,
):
    story = tracking_result["story"]

    print("")
    print("=" * 60)
    print(" 🧵 STORY TRACKER")
    print("=" * 60)

    print(
        f"Story ID: {story.get('story_id')}"
    )

    print(
        f"Topic: {story.get('topic')}"
    )

    print(
        f"Status: {story.get('status')}"
    )

    print(
        f"Articles tracked: "
        f"{len(story.get('articles', []))}"
    )

    print(
        f"Sources tracked: "
        f"{len(story.get('sources', []))}"
    )

    print(
        f"Developments: "
        f"{len(story.get('developments', []))}"
    )

    new_count = len(
        tracking_result.get(
            "new_developments",
            [],
        )
    )

    print(
        f"New developments this run: "
        f"{new_count}"
    )

    if new_count:

        print("")
        print("🆕 NEW DEVELOPMENTS")

        for item in tracking_result[
            "new_developments"
        ]:
            print(
                f"• {item.get('title')}"
            )
def refresh_active_story(story):
    """
    Search an already active story for new developments.
    """

    print("")
    print("=" * 60)
    print(
        f" 🔄 REFRESHING STORY: "
        f"{story.get('topic')}"
    )
    print("=" * 60)

    articles = search_active_story(
        story
    )

    print(
        f"📰 New search returned "
        f"{len(articles)} articles."
    )

    if not articles:
        return {
            "story": story,
            "articles_found": 0,
            "new_developments": [],
            "results": [],
        }

    stories = load_active_stories()

    results = update_stories_with_articles(
        stories,
        articles,
    )

    new_developments = (
        get_new_developments(
            results
        )
    )

    save_active_stories(
        stories
    )

    # Story object refresh करें
    for saved_story in stories:
        if (
            saved_story.get("story_id")
            == story.get("story_id")
        ):
            story = saved_story
            break

    return {
        "story": story,
        "articles_found": len(articles),
        "new_developments": new_developments,
        "results": results,
    }
