from trends import get_top_topics


def main():

    print("===================================")
    print(" Facebook Content Automation")
    print("===================================")

    top_topics = get_top_topics(3)

    print("\n🏆 FINAL TOP 3 TOPICS\n")

    if not top_topics:
        print("No suitable topics found.")
        return

    for number, topic in enumerate(top_topics, start=1):

        print(f"\n{number}. {topic['topic']}")
        print(f"   Score: {topic['score']}")
        print(f"   News coverage: {topic['news_count']}")


if __name__ == "__main__":
    main()
