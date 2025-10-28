import json, subprocess

def probe_duration_seconds(input_url: str) -> int | None:
    """
    Возвращает длительность в секундах, либо None при ошибке.
    Требует установленный ffmpeg/ffprobe в системе.
    """
    try:
        # -v error — только ошибки; -of json — удобный парсинг
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            input_url
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=30)
        payload = json.loads(out)
        dur = float(payload["format"]["duration"])
        return int(round(dur))
    except Exception:
        return None