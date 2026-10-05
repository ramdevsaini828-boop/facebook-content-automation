import os
import requests


GRAPH_API_VERSION = "v23.0"


def get_page_credentials():
    """
    Read Facebook credentials from environment variables.
    """

    page_id = os.getenv("FACEBOOK_PAGE_ID")
    page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

    if not page_id or not page_access_token:
        return None, None

    return page_id, page_access_token


def publish_to_facebook(message):
    """
    Publish a text post to a Facebook Page.
    """

    page_id, page_access_token = get_page_credentials()

    if not page_id or not page_access_token:
        print("⚠️ Facebook credentials not configured.")
        print("Post was NOT published.")
        return {
            "success": False,
            "published": False,
            "reason": "missing_credentials",
        }

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/{page_id}/feed"
    )

    payload = {
        "message": message,
        "access_token": page_access_token,
    }

    try:
        response = requests.post(
            url,
            data=payload,
            timeout=30,
        )

        data = response.json()

        if response.ok and "id" in data:
            print("✅ Facebook post published.")
            print(f"Post ID: {data['id']}")

            return {
                "success": True,
                "published": True,
                "post_id": data["id"],
            }

        print("❌ Facebook publishing failed.")
        print(data)

        return {
            "success": False,
            "published": False,
            "response": data,
        }

    except requests.RequestException as error:
        print("❌ Facebook API request failed.")
        print(error)

        return {
            "success": False,
            "published": False,
            "reason": str(error),
        }
