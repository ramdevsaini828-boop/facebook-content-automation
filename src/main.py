from research import (
    collect_research,
    print_research_articles,
    analyze_research,
)
from trends import get_top_topics
from news import analyze_topic
from event_ranker import (
    rank_events,
    print_ranked_events
)


def main():

    print("===================================")
    print(" Facebook Content Automation")
    print("===================================")

    top_topics = get_top_topics(3)

    print("\n🏆 TOP 3 TRENDING TOPICS\n")

    if not top_topics:
        print("No suitable topics found.")
        return

    analyses = []

    for number, topic_data in enumerate(
        top_topics,
        start=1
    ):

        topic = topic_data["topic"]

        print("\n" + "#" * 60)
        print(
            f"TOPIC {number}: {topic}"
        )
        print("#" * 60)

        result = analyze_topic(topic)

        analyses.append(result)

    print("\n\n")
    print("=" * 60)
    print(" EVENT RANKING")
    print("=" * 60)

    final_events = []

    for result in analyses:

        topic = result["topic"]
        articles = result["articles"]

        print("\n")
        print(f"📌 TOPIC: {topic}")

        if not articles:

            print(
                "❌ Not enough fresh news"
            )

            continue

        events = rank_events(articles)

        print_ranked_events(events)

        if events:

            strongest_event = events[0]

            final_events.append({
                "topic": topic,
                "event": strongest_event
            })


    print("\n\n")
    print("=" * 60)
    print(" 🏆 STRONGEST EVENT FOR EACH TOPIC")
    print("=" * 60)
# ==========================================
# STEP 6D - DEEP RESEARCH
# ==========================================

print("\n\n🔬 Starting deep research...")

research_articles = collect_research(
    topic,
    strongest_event
)

print_research_articles(
    research_articles
)

research_data = analyze_research(
    topic,
    strongest_event,
    research_articles
)

print("\n📊 RESEARCH SUMMARY")
print(
    f"Articles: {research_data['article_count']}"
)
print(
    f"Sources: {research_data['source_count']}"
)
    for item in final_events:

        topic = item["topic"]
        event = item["event"]

        print("\n" + "-" * 60)

        print(
            f"TOPIC: {topic}"
        )

        print(
            f"EVENT SCORE: "
            f"{event['score']}"
        )

        print(
            "EVENT KEYWORDS: "
            + ", ".join(
                event["keywords"][:8]
            )
        )

        print(
            f"SUPPORTING ARTICLES: "
            f"{len(event['articles'])}"
        )

        print("\nTOP HEADLINES:")

        for article in event["articles"][:5]:

            print(
                f"- {article['title']}"
            )

            print(
                f"  Source: "
                f"{article['source']}"
            )

            print(
                f"  Published: "
                f"{article['published']}"
            )


if __name__ == "__main__":
    main()
