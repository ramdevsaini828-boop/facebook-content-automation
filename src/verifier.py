import re
import requests
import trafilatura


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    )
}


def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def fetch_article_text(url):
    """
    Try to download and extract the main article text.
    """

    if not url:
        return None

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=25,
            allow_redirects=True
        )

        response.raise_for_status()

        html = response.text

        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            include_links=False
        )

        if not text:
            return None

        return clean_text(text)

    except Exception as error:

        print(
            f"⚠️ Article extraction failed: "
            f"{url}"
        )

        print(
            f"   Reason: {error}"
        )

        return None


def find_relevant_sentences(
    article_text,
    keywords,
    limit=8
):

    if not article_text:
        return []

    sentences = re.split(
        r"(?<=[.!?।])\s+",
        article_text
    )

    keyword_list = []

    for keyword in keywords:

        keyword = clean_text(
            keyword.lower()
        )

        if keyword:
            keyword_list.append(
                keyword
            )

    results = []

    for sentence in sentences:

        sentence_clean = clean_text(
            sentence
        )

        if not sentence_clean:
            continue

        sentence_lower = (
            sentence_clean.lower()
        )

        matches = 0

        for keyword in keyword_list:

            if keyword in sentence_lower:
                matches += 1

        if matches > 0:

            results.append({
                "sentence": sentence_clean,
                "matches": matches,
            })

    results.sort(
        key=lambda x: x["matches"],
        reverse=True
    )

    return [
        item["sentence"]
        for item in results[:limit]
    ]


def verify_article(article, keywords):

    url = article.get("link")

    print("\n🔎 VERIFYING SOURCE")

    print(
        f"Source: "
        f"{article.get('source', 'Unknown')}"
    )

    print(
        f"Title: "
        f"{article.get('title', '')}"
    )

    text = fetch_article_text(url)

    if not text:

        return {
            "title": article.get("title"),
            "source": article.get("source"),
            "url": url,
            "verified": False,
            "verification_status": "TEXT_NOT_AVAILABLE",
            "article_text": "",
            "relevant_sentences": [],
        }

    relevant_sentences = (
        find_relevant_sentences(
            text,
            keywords
        )
    )

    return {
        "title": article.get("title"),
        "source": article.get("source"),
        "url": url,
        "verified": True,
        "verification_status": (
            "TEXT_EXTRACTED"
        ),
        "article_text": text,
        "relevant_sentences": (
            relevant_sentences
        ),
    }


def verify_research_articles(
    articles,
    keywords,
    max_articles=10
):

    verified = []

    print("\n" + "=" * 60)
    print(" 🔬 SOURCE VERIFICATION")
    print("=" * 60)

    for article in articles[:max_articles]:

        result = verify_article(
            article,
            keywords
        )

        verified.append(result)

        if result["verified"]:

            print(
                "   ✅ Article text extracted"
            )

            print(
                f"   Relevant passages: "
                f"{len(result['relevant_sentences'])}"
            )

        else:

            print(
                "   ⚠️ Article text unavailable"
            )

    return verified
