#!/usr/bin/env python

import sys

import EbsSsd
import LocalSsd


def main(argv):
	#EbsSsd.Setup()
	#EbsSsd.Run()

	#LocalSsd.Setup()
	LocalSsd.Run()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
