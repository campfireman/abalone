#!/usr/bin/env python
# -*- coding: utf-8 -*-


if __name__ == '__main__':  # pragma: no cover
    # Run a game from the command line with default configuration.
    import argparse
    import importlib
    import sys

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('exp_name', metavar='exp', type=str,
                        help='Name of the python experiment to run')

    args = parser.parse_args()

    exp = getattr(importlib.import_module(
        f'src.experiments.{args.exp_name}'), 'main')
    exp()
