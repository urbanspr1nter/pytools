import argparse
from pathlib import Path

"""
@Author: urbanspr1nter@gmail.com
@Date: 2023-07-05
"""


def clear_svg(current_path: Path):
    """
    Recursively digs into the given path and finds all SVG files to replace
    its contents with an empty string so that the .svg file itself becomes
    empty.
    :param current_path: Path object
    :return:
    """
    if current_path.is_file() and current_path.name.endswith(".svg"):
        print(f"🧹\tRemoving contents of {current_path} file.")
        with current_path.open(mode="w") as f:
            f.write("")
            f.close()
    elif current_path.is_dir():
        for child_path in current_path.iterdir():
            clear_svg(child_path)

    return


parser = argparse.ArgumentParser(description="Removes SVG content given a path")
parser.add_argument("--start_path", metavar="START_PATH", type=str, help="Root path", required=True, nargs=1)

args = parser.parse_args()

try:
    start_path = args.start_path.pop()
    print(f"⭐\tUsing provided path: {start_path}")
    start_path_as_path = Path(start_path)
    clear_svg(start_path_as_path)
    print("✅\tAll done!")
except Exception as e:
    print("❌\tError occurred.")
    print(e.args)
