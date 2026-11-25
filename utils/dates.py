from datetime import date, timedelta

PRESETS = {"1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}

def default_range():
    end = date.today()
    start = end - timedelta(days=30)
    return start, end
