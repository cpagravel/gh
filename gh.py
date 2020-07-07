#! /usr/bin/env python3
# Lint as: python3

import argparse
from collections import OrderedDict
import logging
import os
import re
import subprocess
import sys

from typing import Callable, List, Union

ITEMS_TO_SHOW = 10
DEBUG = False

LOGGER = logging.getLogger(__name__)
sh = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(sh)
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False

# credit: https://stackoverflow.com/questions/3305287/python-how-do-you-view-output-that-doesnt-fit-the-screen
# slight modification
class Less(object):
    def __init__(self, num_lines: int=40):
        self.num_lines = num_lines
    def __ror__(self, msg: str):
        if (len(msg.split("\n")) <= self.num_lines):
            LOGGER.info(msg)
        else:
            with subprocess.Popen(["less", "-R"], stdin=subprocess.PIPE) as less:
                try:
                    less.stdin.write(msg.encode("utf-8"))
                    less.stdin.close()
                    less.wait()
                except KeyboardInterrupt:
                    less.kill()
                    bash("stty echo")


class Colors(object):
    BLUE        = "\033[1;34m"
    BOLD        = "\033[;1m"
    CYAN        = "\033[1;36m"
    GREEN       = "\033[1;32m"
    OFF         = "\033[1;;m"
    PURPLE      = "\033[1;35m"
    RED         = "\033[1;31m"
    RESET       = "\033[0;0m"
    REVERSE     = "\033[;7m"
    WHITE       = "\033[1;37m"
    YELLOW      = "\033[1;33m"

    @staticmethod
    def colorize(text, color):
        return color + str(text) + Colors.OFF

def bash(command: Union[List[str], str]):
    if ("list" in str(type(command))):
        command_array = [cmd.replace('"', '') for cmd in command]
    else:
        command_array = command.split()
    LOGGER.debug("Bash: %s", " ".join(command_array))
    proc = subprocess.Popen(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    (output, err) = proc.communicate()
    return (output, err)

def generateHistoryList() -> List[str]:
    (output, err) = bash("git reflog show")
    if (len(err) != 0):
        raise RuntimeError(err.decode("utf-8"))
    output = [line for line in output.decode().split("\n") if "checkout:" in line]
    checkout_targets = re.findall(r"checkout: moving from ([^ ]+) to (?:[^ ]+)", "\n".join(output))
    (current_branch, _) = bash("git rev-parse --abbrev-ref HEAD")
    current_branch = current_branch.decode().strip()

    checkout_set = OrderedDict()
    checkout_set[current_branch] = 1
    for target in checkout_targets:
        checkout_set[target] = 1
    return list(checkout_set.keys())

def displayList(checkout_history, verbose=False):
    header = Colors.colorize("#   BRANCH HISTORY", Colors.YELLOW)
    LOGGER.info(header)
    for (index, branch) in enumerate(checkout_history):
        if not verbose and index > ITEMS_TO_SHOW:
            break
        index = Colors.colorize(index, Colors.PURPLE)
        branch = Colors.colorize(branch, Colors.GREEN)
        LOGGER.info("{:<16} {:<21} ({})".format(index, branch, index))

def checkValidRef(item_count: int) -> Callable[[Union[str, int]], int]:
    def _checkValidRef(ref: Union[str, int]) -> int:
        ref = int(ref)
        if ref < 0:
            raise argparse.ArgumentTypeError("%s is an invalid positive int value" % ref)
        elif ref > item_count:
            raise argparse.ArgumentTypeError("%s is an out of range" % ref)
        return ref
    return _checkValidRef

def main():
    try:
        checkout_history = generateHistoryList()
    except RuntimeError as e:
        LOGGER.info(e)
        exit(1)
    checkout_history.pop(0)  # Pop the branch that we"re currently on
    item_count = len(checkout_history)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="show all branch references in history")
    parser.add_argument("--debug", action="store_true", help="show bash commands")

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "REF", metavar="REF_INT", type=checkValidRef(item_count), nargs="?",
        help="Output the branch reference in checkout history")
    group.add_argument(
        "-c", type=checkValidRef(item_count), metavar="REF_INT",
        dest="checkout", help=("eq to " + Colors.colorize("git checkout ", Colors.GREEN)
        + Colors.colorize("<BRANCH_REF>", Colors.RED)))

    args = parser.parse_args()

    if args.debug:
        LOGGER.setLevel(logging.DEBUG)

    if args.REF is not None:  # print branch name
        LOGGER.info(checkout_history[args.REF])
    elif args.checkout is not None:  # checkout branch
        command = f"git checkout {checkout_history[args.checkout]}"
        (output, err) = bash(command)
        if err:
            LOGGER.error(err.decode())
        LOGGER.info(output.decode())
    else:
        displayList(checkout_history, args.verbose)

if __name__ == "__main__":
    main()
