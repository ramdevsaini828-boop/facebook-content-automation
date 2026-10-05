import requests
import xml.etree.ElementTree as ET


GOOGLE_TRENDS_RSS = "https://trends.google.com/trending/rss?geo=IN&hl=en-US"


def get_google_trends(limit=20):
    """
    India ke current Google Trends topics fetch karta hai.
    """

    try:
        response = requests.get(
            GOOGLE_TRENDS_RSS,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        root = ET.fromstring(response.content)

        topics = []

        for item in root.findall(".//item"):
            title = item.findtext("title")
            link = item.findtext("link")
            description = item.findtext("description")

            if title:
                topics.append({
                    "topic": title.strip(),
                    "link": link,
                    "description": description
                })

            if len(topics) >= limit:
                break

        return topics

    except Exception as error:
        print(f"Google Trends error: {error}")
        return []


if __name__ == "__main__":
    trends = get_google_trends()

    print("\n🔥 INDIA TRENDING TOPICS\n")

    for number, trend in enumerate(trends, start=1):
        print(f"{number}. {trend['topic']}")
