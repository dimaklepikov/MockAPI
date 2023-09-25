import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', action='store', required=False)

    return parser.parse_known_args()
