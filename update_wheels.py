"""
Update the wheels in this repository.  This script will automatically update
the wheels in this repository after a new set of wheels were copy-pasted
into the directory.

Usage:
    update_wheels.py (-h | --help)
    update_wheels.py [--dry-run]

Options:
    -h --help     Prints this documentation
    -n --dry-run  Prints the commands without running them
"""
import logging

import docopt

import git


def main():
    args = docopt.docopt()
