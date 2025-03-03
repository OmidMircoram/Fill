import argparse


def main():
    """Entrypoiny"""


parser = argparse.ArgumentParser("Phill")
parser.add_argument(
    "--view",
    "-v",
    help="Decide wheater to run the web app or just run the calculations",
    type=bool,
)
args = parser.parse_args()
opts = args.method

print(opts)
