import argparse
import base64

"""
@Author: urbanspr1nter@gmail.com
@Date: 2023-07-06
"""


def stob64(input_str: str):
    """
    Converts any input string to a base64 encoded string.
    :param input_str:
    :return:
    """
    b64_str = base64.b64encode(bytes(input_str, "utf-8"))
    return b64_str.decode("utf-8")


parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    metavar="VALUE_STRING",
    type=str, required=True,
    nargs=1,
    help="input string to be converted to base64")

args = parser.parse_args()

value_string = args.input.pop()

print(stob64(value_string))
