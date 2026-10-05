import json
from datetime import datetime


def build_facebook_post(
    topic,
    event,
    research_data,
    evidence_data=None,
    verified_articles=None,
):
    """
    Build a structured Facebook post from the research pipeline.

    This version does not call a paid AI API.
    It creates a safe structured draft that can later
    be connected to an AI model.
    """

    keywords = event.get("keywords", [])

    headlines = []

    for article in event.get("articles", [])[:5]:
        title = article.get("title", "").strip()

        if title:
            headlines.append(title)

    sources = []

    for article in research_data.get("articles", [])[:10]:
        source = article.get("source", "").strip()

        if source and source not in sources:
            sources.append(source)

    post = []

    post.append(f"📰 {topic}")
    post.append("")
    post.append("क्या हुआ?")
    post.append("")

    if headlines:
        post.append(
            "इस समय इस विषय से जुड़ी कई रिपोर्ट्स और developments सामने आ रही हैं।"
        )

        for headline in headlines[:3]:
            post.append(f"• {headline}")
    else:
        post.append(
            "इस विषय पर उपलब्ध research और news reports के आधार पर "
            "मामले पर लगातार developments सामने आ रहे हैं।"
        )

    post.append("")
    post.append("🔎 मुख्य बिंदु")
    post.append("")

    if keywords:
        post.append(
            "इस घटना से जुड़े प्रमुख keywords: "
            + ", ".join(keywords[:8])
        )

    post.append("")
    post.append("📌 क्या ध्यान रखना जरूरी है?")
    post.append("")
    post.append(
        "उपलब्ध reports में कुछ बातें सीधे reported developments हैं, "
        "जबकि कुछ claims या reports के रूप में सामने आती हैं। "
        "इसलिए हर दावे को confirmed fact मानना उचित नहीं होगा।"
    )

    post.append("")
    post.append("⚖️ संतुलित नजरिया")
    post.append("")
    post.append(
        "इस विषय को समझने के लिए केवल एक headline देखने के बजाय "
        "अलग-अलग credible sources और उपलब्ध evidence को साथ देखना जरूरी है।"
    )

    post.append("")
    post.append("🔮 आगे क्या हो सकता है?")
    post.append("")
    post.append(
        "आगे की स्थिति आने वाली official updates, verified reports "
        "और ground-level developments पर निर्भर करेगी।"
    )

    post.append("")
    post.append("🧾 Sources")
    post.append("")

    if sources:
        for source in sources[:8]:
            post.append(f"• {source}")
    else:
        post.append("• Research sources collected during automation")

    post.append("")
    post.append("💡 निष्कर्ष")
    post.append("")
    post.append(
        "इस मुद्दे पर जल्दबाजी में निष्कर्ष निकालने के बजाय "
        "verified information और multiple sources के आधार पर राय बनाना बेहतर है।"
    )

    post.append("")
    post.append("#News #India #Analysis")

    return "\n".join(post)


def save_post(post, topic):
    """
    Save generated Facebook post locally.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    safe_topic = "".join(
        character if character.isalnum() else "_"
        for character in topic
    )

    filename = f"output/facebook_post_{safe_topic}_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(post)

    return filename


def save_post_json(post, topic, event):
    """
    Save structured post data as JSON.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    safe_topic = "".join(
        character if character.isalnum() else "_"
        for character in topic
    )

    filename = f"output/facebook_post_{safe_topic}_{timestamp}.json"

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
            indent=2
        )

    return filename
