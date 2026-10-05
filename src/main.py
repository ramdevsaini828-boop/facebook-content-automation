from trends import get_google_trends


def main():
    print("===================================")
    print(" Facebook Content Automation")
    print("===================================")

    trends = get_google_trends(limit=20)

    print("\n🔥 CURRENT INDIA TRENDS\n")

    if not trends:
        print("No trends found.")
        return

    for number, trend in enumerate(trends, start=1):
        print(f"{number}. {trend['topic']}")


if __name__ == "__main__":
    main()
