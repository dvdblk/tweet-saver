from datetime import datetime
from zoneinfo import ZoneInfo


def fmt_created_at(d: datetime = datetime.now()) -> str:
    """Create a formatted string from datetime in GMT+2"""
    return d.astimezone(ZoneInfo("Europe/Zurich")).strftime(
        "%H:%M:%S • %d/%m/%Y",
    )
