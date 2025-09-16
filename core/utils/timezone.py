from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+ 內建


def utc_to_local(utc_input, tz_name: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    將 UTC 時間 (字串或 datetime) 轉換成指定時區的時間字串

    :param utc_input: UTC 時間，可以是 str 或 datetime
                      - str 格式: "YYYY-MM-DD HH:MM:SS" 或 "YYYY-MM-DD HH:MM:SS.ssssss"
                      - datetime 格式: 必須是 naive (視為 UTC) 或 tz-aware (UTC)
    :param tz_name: 時區名稱，例如 "Asia/Taipei"
    :param fmt: 輸出格式 (預設: %Y-%m-%d %H:%M:%S)
    :return: 指定時區的時間字串
    """
    # 如果是字串
    if isinstance(utc_input, str):
        try:
            utc_dt = datetime.strptime(utc_input, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            utc_dt = datetime.strptime(utc_input, "%Y-%m-%d %H:%M:%S")
        utc_dt = utc_dt.replace(tzinfo=ZoneInfo("UTC"))
    # 如果是 datetime
    elif isinstance(utc_input, datetime):
        if utc_input.tzinfo is None:
            utc_dt = utc_input.replace(tzinfo=ZoneInfo("UTC"))
        else:
            utc_dt = utc_input.astimezone(ZoneInfo("UTC"))
    else:
        raise TypeError("utc_input 必須是 str 或 datetime.datetime")

    local_dt = utc_dt.astimezone(ZoneInfo(tz_name))
    return local_dt.strftime(fmt)
