"""国土地理院のAPIを使って緯度経度から標高を得る"""
from pathlib import Path
from datetime import datetime
from gpxpy.gpx import GPX
import time
import argparse
from func import open_file, save_cache, load_cache, to_local_time, get_ele_from_gsi


PWD = Path(__file__).parent


def parse_gpx(gpx: GPX, accuracy: int, interval: int):
    try:
        cache = load_cache()
    except FileNotFoundError:
        cache = dict()
    for track in gpx.tracks:
        for segment in track.segments:
            points = []
            last_point = None
            for point in segment.points:
                if last_point is None:
                    last_point = point
                if point != last_point and point.time_difference(last_point) < interval:
                    continue
                last_point = point
                points.append(point)
                if point.time is not None:
                    point.time = to_local_time(point.time)
                if accuracy >= 0:
                    rounded_latitude = round(point.latitude, accuracy)
                    rounded_longitude = round(point.longitude, accuracy)
                    point.latitude = rounded_latitude
                    point.longitude = rounded_longitude
                    elevation = cache.get((rounded_latitude, rounded_longitude))
                    if elevation is not None:
                        point.elevation = elevation
                    else:
                        point.elevation = get_ele_from_gsi(rounded_latitude, rounded_longitude)
                        save_cache(rounded_latitude, rounded_longitude, point.elevation)
                        cache[(rounded_latitude, rounded_longitude)] = point.elevation
                        time.sleep(0.2)
            segment.points = points


def process_gpx(file: Path, output_dir: Path, accuracy: int=-1, interval: int=-1):
    gpx = open_file(file)

    parse_gpx(gpx, accuracy, interval)

    output_path = output_dir / f"{file.stem}.gpx"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(gpx.to_xml())

    print(f"Saved: {output_path}")



def main():
    parser = argparse.ArgumentParser(
        description="""
comapsからエクスポートしたgpxファイルを編集するためのスクリプト
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-f",
        required=True,
        help="Input file or directory"
    )

    parser.add_argument(
        "-o",
        default=PWD / "output",
        help="出力先フォルダ(デフォルト: output)"
    )

    parser.add_argument(
        "--adjust-elevation-accuracy",
        default=100,
        help="国土地理院のデータをもとに<ele>(標高)を補正する。小数点以下の桁数を指定する。4桁で11m, 5桁で1.1m, 6桁で0.1m。デフォルトは100(補正しない)"
    )

    parser.add_argument(
        "--time-interval",
        default=-1,
        help="ポイント間の時間が指定の秒数になるように間引く。デフォルトは-1(間引かない)"
    )

    args = parser.parse_args()

    input_path = Path(args.f)
    output_dir = Path(args.o)
    try:
        accuracy = int(args.adjust_elevation_accuracy)
    except ValueError:
        print("--adjust-elevation-accuracyは整数で指定してください")
        return
    try:
        interval = int(args.time_interval)
    except ValueError:
        print("--time-intervalは整数で指定してください")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_dir():
        files = sorted(input_path.glob("*.gpx"))
    elif input_path.is_file():
        files = [input_path]
    else:
        parser.error(f"Input path does not exist: {input_path}")

    for file in files:
        process_gpx(file, output_dir, accuracy, interval)


if __name__ == "__main__":
    main()

                