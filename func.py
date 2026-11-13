from pathlib import Path
from datetime import datetime
import requests
import gpxpy
from gpxpy.gpx import GPX

CACHE_PATH = Path(__file__).parent / ".cache"

def open_file(path: str | Path):
    with open(path, "r", encoding="utf-8") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    return gpx

def to_local_time(time: datetime):
    """ローカルタイムゾーンの時刻に変換する"""
    return time.astimezone()


def get_datetime_from_gpx_data(gpx: GPX):
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if point.time is not None:
                    time_jst = to_local_time(point.time)
                    return time_jst.strftime("%Y-%m-%d_%H_%M")

def save_cache(lat: float, lon: float, ele: float):
    with open(CACHE_PATH, "a") as f:
        f.write(f"{lat},{lon},{ele}\n")

    return

def load_cache():
    with open(CACHE_PATH, "r") as f:
        cache = dict()
        for line in f:
            lat, lon, ele = map(float, line.strip().split(","))
            cache[(lat, lon)] = ele

    return cache



def get_ele_from_gsi(lat: float, lon: float):
    """国土地理院のAPIを使って緯度経度から標高を得る"""

    url = "https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php"
    response = requests.get(url, params={"lon": lon, "lat": lat}, timeout=5)

    data = response.json()
    elevation = data.get("elevation")

    return elevation
