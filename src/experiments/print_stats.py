#!/usr/bin/env python
from ..utils import GameStats

if __name__ == '__main__':  # pragma: no cover
    # Run a game from the command line with default configuration.
    import argparse
    import importlib
    import sys

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('filename', metavar='name', type=str,
                        help='Name of the file')
    args = parser.parse_args()
    GameStats.print(args.filename + '.pickle')
