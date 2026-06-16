from datetime import UTC, datetime


def build_click_event(short_code: str, original_url: str) -> dict[str, str]:
    """Analytics event published when a short URL is visited."""
    return {
        "short_code": short_code,
        "original_url": original_url,
        "clicked_at": datetime.now(UTC).isoformat(),
    }
