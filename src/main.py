from trends import get_top_topics
from news import analyze_topic


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

    for number, topic_data in enumerate(top_topics, start=1):

        topic = topic_data["topic"]

        print(f"\n{'#' * 60}")
        print(f"TOPIC {number}: {topic}")
        print(f"{'#' * 60}")

        result = analyze_topic(topic)

        analyses.append(result)

    print("\n\n===================================")
    print(" EVENT ANALYSIS COMPLETE")
    print("===================================")

    for result in analyses:

        print(f"\n📌 {result['topic']}")

        if not result["articles"]:
            print("   ❌ Not enough fresh news")
            continue

        print(
            f"   📰 Fresh articles: "
            f"{len(result['articles'])}"
        )

        print("   🔥 Event signals:")

        for word, count in result["event_signal"][:5]:
            print(f"      {word}: {count}")


if __name__ == "__main__":
    main()
