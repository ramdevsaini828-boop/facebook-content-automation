from story_tracker import (
    track_story,
    print_story_status,
)

from content import (
    build_facebook_post,
    save_post,
    save_post_json,
)

from facebook import (
    publish_to_facebook,
)

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
    print_ranked_events,
)

from research import (
    collect_research,
    analyze_research,
)


def main():

    print("===================================")
    print(" Facebook Content Automation")
    print("===================================")

    # ==========================================
    # STEP 1 - GET TOP 3 TRENDING TOPICS
    # ==========================================

    top_topics = get_top_topics(3)

    print("\n🏆 TOP 3 TRENDING TOPICS\n")

    if not top_topics:

        print("No suitable topics found.")

        return

    analyses = []

    # ==========================================
    # STEP 2 - ANALYZE TOPICS
    # ==========================================

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

    # ==========================================
    # STEP 3 - EVENT RANKING
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
        print(
            f"📌 TOPIC: {topic}"
        )

        if not articles:

            print(
                "❌ Not enough fresh news"
            )

            continue

        events = rank_events(
            articles
        )

        print_ranked_events(
            events
        )

        if events:

            strongest_event = events[0]

            final_events.append({
                "topic": topic,
                "event": strongest_event,
            })

    # ==========================================
    # STEP 4 - STRONGEST EVENT FOR EACH TOPIC
    # ==========================================

    print("\n\n")
    print("=" * 60)
    print(
        " 🏆 STRONGEST EVENT FOR EACH TOPIC"
    )
    print("=" * 60)

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

    # ==========================================
    # STEP 6D - DEEP RESEARCH
    # ==========================================

    print("\n\n")
    print("=" * 60)
    print(
        " 🔬 STEP 6D - DEEP RESEARCH"
    )
    print("=" * 60)

    for item in final_events:

        topic = item["topic"]

        strongest_event = item["event"]

        print("\n")
        print("#" * 60)

        print(
            f"🔬 RESEARCHING: {topic}"
        )

        print("#" * 60)

        # ------------------------------------------
        # COLLECT RESEARCH ARTICLES
        # ------------------------------------------

        research_articles = collect_research(
            topic,
            strongest_event
        )

        # ------------------------------------------
        # PRINT RESEARCH ARTICLES
        # ------------------------------------------

        # ------------------------------------------
        # ANALYZE RESEARCH
        # ------------------------------------------

        research_data = analyze_research(
            topic,
            strongest_event,
            research_articles
        )

        print(
            "\n📊 RESEARCH SUMMARY"
        )

        print(
            f"Articles: "
            f"{research_data['article_count']}"
        )

        print(
            f"Sources: "
            f"{research_data['source_count']}"
        )

        # ==========================================
        # STEP 6E - EVIDENCE EXTRACTION
        # ==========================================

        print("\n")
        print("=" * 60)

        print(
            " 🧾 STEP 6E - EVIDENCE EXTRACTION"
        )

        print("=" * 60)

        evidence_data = build_evidence_dataset(
            topic,
            strongest_event,
            research_articles
        )

        print_evidence_dataset(
            evidence_data
        )

        # ==========================================
        # STEP 6F - SOURCE VERIFICATION
        # ==========================================

        print("\n")
        print("=" * 60)

        print(
            " 🔎 STEP 6F - SOURCE VERIFICATION"
        )

        print("=" * 60)

        verified_articles = (
            verify_research_articles(
                research_articles,
                strongest_event.get(
                    "keywords",
                    []
                ),
                max_articles=10
            )
        )

        # ------------------------------------------
        # VERIFICATION SUMMARY
        # ------------------------------------------
        # STEP 7 - FACEBOOK CONTENT GENERATION
        print("\n")
        print("=" * 60)
        print(" ✍️ STEP 7 - FACEBOOK CONTENT GENERATION")
        print("=" * 60)

        post = build_facebook_post(
            topic,
            strongest_event,
            research_data,
            evidence_data,
            verified_articles,
        )

        print("\n📝 GENERATED FACEBOOK POST\n")
        print(post)

        # STEP 7A - SAVE POST
        text_file = save_post(
            post,
            topic
        )

        json_file = save_post_json(
            post,
            topic,
            strongest_event
        )

        print("\n💾 POST SAVED")
        print(f"Text: {text_file}")
        print(f"JSON: {json_file}")

        # STEP 8 - FACEBOOK PUBLISH
        print("\n")
        print("=" * 60)
        print(" 📤 STEP 8 - FACEBOOK PUBLISH")
        print("=" * 60)

        publish_result = publish_to_facebook(post)

        if publish_result["published"]:
            print("✅ Published successfully.")
        else:
            print("ℹ️ Facebook post not published.")

                # STEP 9 - CONTINUOUS STORY TRACKING
        print("\n")
        print("=" * 60)
        print(" 🧵 STEP 9 - CONTINUOUS STORY TRACKING")
        print("=" * 60)

        tracking_result = track_story(
            topic,
            strongest_event,
            research_data.get(
                "articles",
                []
            ),
        )

        print_story_status(
            tracking_result
        )
        print(
            "\n📊 VERIFICATION SUMMARY"
        )

        verified_count = sum(
            1
            for article in verified_articles
            if article["verified"]
        )

        unavailable_count = (
            len(verified_articles)
            - verified_count
        )

        print(
            f"Articles checked: "
            f"{len(verified_articles)}"
        )

        print(
            f"Article text extracted: "
            f"{verified_count}"
        )

        print(
            f"Article text unavailable: "
            f"{unavailable_count}"
        )

    # ==========================================
    # AUTOMATION FINISHED
    # ==========================================

    print("\n\n")
    print("=" * 60)

    print(
        " ✅ AUTOMATION RUN COMPLETED"
    )

    print("=" * 60)


# ==========================================
# PROGRAM ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()
