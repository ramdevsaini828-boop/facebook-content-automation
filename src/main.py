from verifier import (
    verify_research_articles,
)

from evidence import (
    build_evidence_dataset,
    print_evidence_dataset,
)

from trends import get_top_topics
from news import analyze_topic
from event_ranker import (
    rank_events,
    print_ranked_events
)
from research import (
    collect_research,
    print_research_articles,
    analyze_research,
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

    # ==========================================
    # STEP 1 - ANALYZE TOPICS
    # ==========================================

    for number, topic_data in enumerate(
        top_topics,
        start=1
    ):

        topic = topic_data["topic"]

        print("\n" + "#" * 60)
        print(f"TOPIC {number}: {topic}")
        print("#" * 60)

        result = analyze_topic(topic)

        analyses.append(result)

    # ==========================================
    # STEP 2 - EVENT RANKING
    # ==========================================

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

            print("❌ Not enough fresh news")

            continue

        events = rank_events(articles)

        print_ranked_events(events)

        if events:

            strongest_event = events[0]

            final_events.append({
                "topic": topic,
                "event": strongest_event
            })

    # ==========================================
    # STEP 3 - STRONGEST EVENTS
    # ==========================================

    print("\n\n")
    print("=" * 60)
    print(" 🏆 STRONGEST EVENT FOR EACH TOPIC")
    print("=" * 60)

    for item in final_events:

        topic = item["topic"]
        event = item["event"]

        print("\n" + "-" * 60)

        print(f"TOPIC: {topic}")

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

    # ==========================================
    # STEP 6D - DEEP RESEARCH
    # ==========================================

    print("\n\n")
    print("=" * 60)
    print(" 🔬 STEP 6D - DEEP RESEARCH")
    print("=" * 60)

    for item in final_events:

        topic = item["topic"]
        strongest_event = item["event"]

        print("\n")
        print("#" * 60)
        print(f"🔬 RESEARCHING: {topic}")
        print("#" * 60)

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

# ==========================================
# STEP 6E - EVIDENCE EXTRACTION
# ==========================================

evidence_data = build_evidence_dataset(
    topic,
    strongest_event,
    research_articles
)
# ==========================================
# STEP 6F - SOURCE VERIFICATION
# ==========================================

verified_articles = verify_research_articles(
    research_articles,
    strongest_event.get(
        "keywords",
        []
    ),
    max_articles=10
)


print_evidence_dataset(
    evidence_data
)
        
        print("\n📊 RESEARCH SUMMARY")

        print(
            f"Articles: "
            f"{research_data['article_count']}"
        )

        print(
            f"Sources: "
            f"{research_data['source_count']}"
        )


if __name__ == "__main__":
    main()
