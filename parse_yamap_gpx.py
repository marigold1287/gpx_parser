from gpxpy.gpx import GPX
from pathlib import Path
import re
from datetime import datetime
from func import open_file, to_local_time, get_datetime_from_gpx_data
import argparse


PWD = Path(__file__).parent


def parse_gpx(gpx: GPX):
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if point.time is not None:
                    point.time = to_local_time(point.time)


def get_datetime_from_filename(filename: str):
    match = re.match(
        r"yamap_([0-9]{4}-[012][0-9]-[0123][0-9]_[012][0-9]_[0-6][0-9])(\.gpx)?",
        filename
    )

    if match is None:
        return None

    return match.group(1)


def get_name_from_gpx_data(gpx: GPX):
    for track in gpx.tracks:
        if track.name is not None:
            return track.name

    return None


def process_gpx(file: Path, output_dir: Path):
    gpx = open_file(file)

    dt = (
        get_datetime_from_filename(file.stem)
        or get_datetime_from_gpx_data(gpx)
        or datetime.now().strftime("%Y-%m-%d_%H_%M")
    )

    gpx_name = get_name_from_gpx_data(gpx) or ""

    output_filename = "_".join([dt, gpx_name])

    parse_gpx(gpx)

    output_path = output_dir / f"{output_filename}.gpx"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(gpx.to_xml())

    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="""
yamapからエクスポートしたgpxファイルを
- 各点の時刻をローカルタイムゾーンに合わせる
- 「YYYY-mm-dd_HH_MM_[活動記録のタイトル].gpx」として保存する
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
        help="出力先フォルダ"
    )

    args = parser.parse_args()

    input_path = Path(args.f)
    output_dir = Path(args.o)

    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_dir():
        files = sorted(input_path.glob("*.gpx"))
    elif input_path.is_file():
        files = [input_path]
    else:
        parser.error(f"Input path does not exist: {input_path}")

    for file in files:
        process_gpx(file, output_dir)


if __name__ == "__main__":
    main()