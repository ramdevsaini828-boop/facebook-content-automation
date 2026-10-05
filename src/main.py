from trends import get_top_topics
from news import get_news_articles


def main():

    print("===================================")
    print(" Facebook Content Automation")
    print("===================================")

    top_topics = get_top_topics(3)

    print("\n🏆 TOP 3 TRENDING TOPICS\n")

    if not top_topics:

        print("No suitable topics found.")

        return

    for number, topic_data in enumerate(
        top_topics,
        start=1
    ):

        topic = topic_data["topic"]

        print(
            f"\n{'=' * 50}"
        )

        print(
            f"TOPIC {number}: {topic}"
        )

        print(
            f"{'=' * 50}"
        )

        articles = get_news_articles(
            topic,
            limit=10
        )

        if not articles:

            print(
                "No articles found."
            )

            continue

        for article_number, article in enumerate(
            articles,
            start=1
        ):

            print(
                f"\n{article_number}. "
                f"{article['title']}"
            )

            print(
                f"   Source: "
                f"{article['source']}"
            )

            print(
                f"   Published: "
                f"{article['published']}"
            )

            print(
                f"   Link: "
                f"{article['link']}"
            )


if __name__ == "__main__":

    main()
