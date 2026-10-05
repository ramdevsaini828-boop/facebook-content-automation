import json
import re
from datetime import datetime


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"\s+", " ", str(text))
    return text.strip()


def unique_items(items):
    seen = set()
    result = []

    for item in items:
        item = clean_text(item)
        if not item:
            continue

        key = item.lower()

        if key not in seen:
            seen.add(key)
            result.append(item)

    return result


def get_article_title(article):
    return clean_text(article.get("title", ""))


def get_article_source(article):
    return clean_text(
        article.get("source")
        or article.get("provider")
        or article.get("publisher")
        or ""
    )


def get_article_date(article):
    return clean_text(
        article.get("published")
        or article.get("published_datetime")
        or article.get("date")
        or ""
    )


# ---------------------------------------------------------
# ARTICLE COLLECTION
# ---------------------------------------------------------

def collect_articles(research_data, evidence_data=None, verified_articles=None):
    """
    Collect useful article records from all available research stages.
    """

    articles = []

    # Deep research
    for article in research_data.get("articles", []):
        articles.append(article)

    # Evidence dataset
    if evidence_data:
        if isinstance(evidence_data, dict):
            evidence_articles = evidence_data.get("items", [])
        else:
            evidence_articles = evidence_data

        for article in evidence_articles:
            articles.append(article)

    # Verification results
    if verified_articles:
        for article in verified_articles:
            articles.append(article)

    return articles


def filter_useful_articles(articles):
    """
    Remove obvious low-value material.

    We do NOT try to delete large amounts of output.
    The purpose here is only to stop obvious spam/noise
    from becoming Facebook content.
    """

    blocked_words = [
        "livestream",
        "live stream",
        "watch live",
        "watch online",
        "stream online",
        "scorecard",
        "prediction",
        "horoscope",
        "rashifal",
        "lottery",
    ]

    useful = []

    for article in articles:
        title = get_article_title(article)

        if not title:
            continue

        title_lower = title.lower()

        # Do not automatically reject every article containing
        # "prediction", but obvious streaming spam should go.
        if any(
            word in title_lower
            for word in [
                "livestream",
                "live stream",
                "watch live",
                "watch online",
                "stream online",
            ]
        ):
            continue

        useful.append(article)

    return useful


# ---------------------------------------------------------
# FACT / REPORT EXTRACTION
# ---------------------------------------------------------

def extract_reported_points(articles, limit=8):
    """
    Build points only from actual article headlines.

    IMPORTANT:
    We do not invent facts that are not present in the research.
    """

    points = []

    for article in articles:
        title = get_article_title(article)
        source = get_article_source(article)

        if not title:
            continue

        if source:
            point = f"{title} ({source})"
        else:
            point = title

        points.append(point)

    return unique_items(points)[:limit]


def extract_sources(articles, limit=10):
    sources = []

    for article in articles:
        source = get_article_source(article)

        if source:
            sources.append(source)

    return unique_items(sources)[:limit]


def extract_dates(articles, limit=10):
    dates = []

    for article in articles:
        date = get_article_date(article)

        if date:
            dates.append(date)

    return unique_items(dates)[:limit]


# ---------------------------------------------------------
# STORY STRUCTURE
# ---------------------------------------------------------

def build_story_summary(topic, event, articles):
    """
    Creates a factual summary based only on collected reports.
    """

    keywords = unique_items(event.get("keywords", []))

    points = extract_reported_points(articles, limit=5)

    lines = []

    lines.append(f"इस समय {topic} से जुड़ी कई reports और developments सामने आए हैं।")

    if points:
        lines.append("")
        lines.append("उपलब्ध reports में प्रमुख developments:")
        for point in points[:5]:
            lines.append(f"• {point}")

    if keywords:
        # Only use a small number of meaningful event keywords.
        meaningful_keywords = [
            k for k in keywords
            if len(k) > 3
            and k.lower() not in {
                "prediction",
                "tradingview",
                "guardian",
                "journal",
                "investment",
                "outlook",
                "livestream",
                "streaming",
            }
        ]

        if meaningful_keywords:
            lines.append("")
            lines.append(
                "Research में बार-बार सामने आने वाले विषय: "
                + ", ".join(meaningful_keywords[:6])
            )

    return "\n".join(lines)


# ---------------------------------------------------------
# BALANCED ANALYSIS
# ---------------------------------------------------------

def build_balanced_analysis(articles):
    """
    We intentionally avoid manufacturing पक्ष-विपक्ष.

    If research contains only one-sided reporting,
    we explicitly say that independent confirmation is limited.
    """

    if not articles:
        return (
            "इस समय उपलब्ध research सीमित है। "
            "इसलिए किसी निष्कर्ष को अंतिम तथ्य मानने से पहले "
            "अधिक independent reports और official information का इंतजार करना उचित होगा।"
        )

    sources = extract_sources(articles)

    if len(sources) >= 3:
        return (
            "इस मुद्दे को समझने के लिए अलग-अलग news sources को साथ देखना जरूरी है। "
            "उपलब्ध research में कई sources से reporting मिली है, लेकिन "
            "हर report में दी गई जानकारी का स्वतंत्र verification समान स्तर पर उपलब्ध नहीं है। "
            "इसलिए confirmed information और reported claims को अलग रखना जरूरी है।"
        )

    return (
        "उपलब्ध research में reporting सीमित sources से मिली है। "
        "इसलिए इसे शुरुआती picture के रूप में देखना बेहतर है। "
        "अधिक independent और official information आने के बाद तस्वीर ज्यादा स्पष्ट होगी।"
    )


# ---------------------------------------------------------
# PAST / PRESENT / FUTURE
# ---------------------------------------------------------

def build_timeline_section(articles):
    dates = extract_dates(articles)

    lines = []

    lines.append("🕰️ अतीत → वर्तमान → आगे")

    lines.append("")

    if dates:
        lines.append(
            "उपलब्ध reports अलग-अलग समय पर प्रकाशित हुई हैं, "
            "जिससे यह स्पष्ट है कि यह विषय एक ongoing development के रूप में देखा जा रहा है।"
        )
    else:
        lines.append(
            "Research में पर्याप्त समय-संदर्भ उपलब्ध नहीं है, "
            "इसलिए घटनाक्रम की पूरी timeline अभी तैयार नहीं की जा सकती।"
        )

    lines.append("")
    lines.append(
        "आगे की कहानी में official announcements, नई reports, "
        "ground developments और independent confirmation सबसे महत्वपूर्ण रहेंगे।"
    )

    return "\n".join(lines)


# ---------------------------------------------------------
# MAIN FACEBOOK POST
# ---------------------------------------------------------

def build_facebook_post(
    topic,
    event,
    research_data,
    evidence_data=None,
    verified_articles=None,
):
    """
    Build a research-based Facebook story.

    IMPORTANT:
    This function does not invent facts.
    """

    all_articles = collect_articles(
        research_data,
        evidence_data,
        verified_articles,
    )

    all_articles = filter_useful_articles(all_articles)

    all_articles = unique_article_records(all_articles)

    points = extract_reported_points(all_articles, limit=6)
    sources = extract_sources(all_articles, limit=10)

    post = []

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    post.append(f"📰 {topic}")
    post.append("")

    post.append("क्या हुआ?")
    post.append("")

    post.append(
        build_story_summary(
            topic,
            event,
            all_articles,
        )
    )

    # -----------------------------------------------------
    # IMPORTANT DEVELOPMENTS
    # -----------------------------------------------------

    post.append("")
    post.append("🔎 प्रमुख developments")
    post.append("")

    if points:
        for point in points[:6]:
            post.append(f"• {point}")
    else:
        post.append(
            "अभी उपलब्ध research से पर्याप्त verified details नहीं मिली हैं।"
        )

    # -----------------------------------------------------
    # BALANCED VIEW
    # -----------------------------------------------------

    post.append("")
    post.append("⚖️ संतुलित नजरिया")
    post.append("")

    post.append(
        build_balanced_analysis(all_articles)
    )

    # -----------------------------------------------------
    # TIMELINE
    # -----------------------------------------------------

    post.append("")
    post.append(
        build_timeline_section(all_articles)
    )

    # -----------------------------------------------------
    # WHAT NEXT
    # -----------------------------------------------------

    post.append("")
    post.append("🔮 आगे क्या देखना होगा?")
    post.append("")

    post.append(
        "इस story में आगे आने वाली official updates, "
        "नई credible reports, नए आंकड़े और ground-level developments "
        "महत्वपूर्ण होंगे। नई जानकारी मिलने पर इस story को update किया जाएगा।"
    )

    # -----------------------------------------------------
    # SOURCES
    # -----------------------------------------------------

    post.append("")
    post.append("🧾 Research Sources")
    post.append("")

    if sources:
        for source in sources:
            post.append(f"• {source}")
    else:
        post.append("• Research sources उपलब्ध नहीं हैं।")

    # -----------------------------------------------------
    # CONCLUSION
    # -----------------------------------------------------

    post.append("")
    post.append("💡 निष्कर्ष")
    post.append("")

    post.append(
        "अभी उपलब्ध जानकारी के आधार पर इस story में सामने आए "
        "reported developments को अलग-अलग देखना जरूरी है। "
        "जैसे-जैसे नई और verified information आएगी, "
        "पूरी तस्वीर ज्यादा स्पष्ट होगी।"
    )

    # -----------------------------------------------------
    # FOLLOW STORY NOTICE
    # -----------------------------------------------------

    post.append("")
    post.append(
        "📌 इस खबर से जुड़े अगले developments को लगातार track किया जाएगा।"
    )

    post.append("")
    post.append("#News #India #NewsAnalysis")

    return "\n".join(post)


# ---------------------------------------------------------
# ARTICLE DEDUPLICATION
# ---------------------------------------------------------

def unique_article_records(articles):
    """
    Deduplicate research articles using title + source.
    """

    seen = set()
    result = []

    for article in articles:
        title = get_article_title(article)
        source = get_article_source(article)

        if not title:
            continue

        key = (
            title.lower(),
            source.lower(),
        )

        if key in seen:
            continue

        seen.add(key)
        result.append(article)

    return result


# ---------------------------------------------------------
# SAVE TEXT
# ---------------------------------------------------------

def safe_filename(text):
    text = re.sub(r"[^\w\-]+", "_", text, flags=re.UNICODE)
    return text[:100].strip("_") or "news"


def save_post(post, topic):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = (
        f"output/facebook_post_"
        f"{safe_filename(topic)}_"
        f"{timestamp}.txt"
    )

    with open(filename, "w", encoding="utf-8") as file:
        file.write(post)

    return filename


# ---------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------

def save_post_json(post, topic, event):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = (
        f"output/facebook_post_"
        f"{safe_filename(topic)}_"
        f"{timestamp}.json"
    )

    data = {
        "topic": topic,
        "event_keywords": event.get("keywords", []),
        "generated_at": datetime.now().isoformat(),
        "post": post,
    }

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return filename
