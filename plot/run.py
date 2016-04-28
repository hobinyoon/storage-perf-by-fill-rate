#!/usr/bin/env python

import sys

import Plot


def main(argv):
	Plot.LocalSsd()
	Plot.EbsSsd()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
